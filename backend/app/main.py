import json
import uuid
import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import redis.asyncio as aioredis

from app.config import (
    UPLOAD_DIR,
    OUTPUT_DIR,
    REDIS_URL,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_EXTENSIONS,
    SUPPORTED_LANGUAGES,
)
from app.models import (
    DubbingRequest,
    JobStatus,
    JobStatusResponse,
    LanguageListResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auto Video Dubbing API",
    description="Production-grade video dubbing with AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client: aioredis.Redis | None = None


@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Connected to Redis")


@app.on_event("shutdown")
async def shutdown_event():
    global redis_client
    if redis_client:
        await redis_client.close()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/languages", response_model=LanguageListResponse)
async def get_languages():
    return LanguageListResponse(languages=SUPPORTED_LANGUAGES)


@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}{ext}"

    total_size = 0
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > max_bytes:
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {MAX_UPLOAD_SIZE_MB}MB",
                )
            f.write(chunk)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "size": total_size,
        "path": str(file_path),
    }


@app.post("/api/dub/{file_id}")
async def start_dubbing(file_id: str, request: DubbingRequest):
    upload_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="Uploaded video not found")

    video_path = str(upload_files[0])
    job_id = str(uuid.uuid4())

    job_data = {
        "job_id": job_id,
        "status": JobStatus.QUEUED.value,
        "progress": 0.0,
        "current_stage": "Queued",
        "source_video": video_path,
        "target_language": request.target_language,
        "source_language": request.source_language or "auto",
        "segments": "[]",
        "output_video": "",
        "error": "",
        "total_segments": 0,
        "processed_segments": 0,
    }

    await redis_client.hset(f"job:{job_id}", mapping=job_data)
    await redis_client.lpush("dubbing_queue", job_id)

    logger.info(f"Job {job_id} queued for video {video_path}")

    return {"job_id": job_id, "status": "queued"}


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    job_data = await redis_client.hgetall(f"job:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_data["job_id"],
        status=JobStatus(job_data["status"]),
        progress=float(job_data.get("progress", 0)),
        current_stage=job_data.get("current_stage", "Unknown"),
        error=job_data.get("error", None) or None,
        output_video=job_data.get("output_video", None) or None,
        total_segments=int(job_data.get("total_segments", 0)),
        processed_segments=int(job_data.get("processed_segments", 0)),
    )


@app.get("/api/download/{job_id}")
async def download_video(job_id: str):
    job_data = await redis_client.hgetall(f"job:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_data["status"] != JobStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Job not completed yet")

    output_path = job_data.get("output_video", "")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output video not found")

    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=f"dubbed_{job_id}.mp4",
    )


@app.get("/api/preview/{job_id}")
async def preview_video(job_id: str):
    job_data = await redis_client.hgetall(f"job:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_data["status"] != JobStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Job not completed yet")

    output_path = job_data.get("output_video", "")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output video not found")

    return FileResponse(path=output_path, media_type="video/mp4")


@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()
    try:
        while True:
            job_data = await redis_client.hgetall(f"job:{job_id}")
            if not job_data:
                await websocket.send_json({"error": "Job not found"})
                break

            status_data = {
                "job_id": job_data["job_id"],
                "status": job_data["status"],
                "progress": float(job_data.get("progress", 0)),
                "current_stage": job_data.get("current_stage", "Unknown"),
                "error": job_data.get("error", "") or None,
                "total_segments": int(job_data.get("total_segments", 0)),
                "processed_segments": int(job_data.get("processed_segments", 0)),
            }
            await websocket.send_json(status_data)

            if job_data["status"] in (JobStatus.COMPLETED.value, JobStatus.FAILED.value):
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
