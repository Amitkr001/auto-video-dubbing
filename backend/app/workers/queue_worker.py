import time
import logging
import signal
import sys

import redis

from app.config import REDIS_URL
from app.pipeline.dubbing_pipeline import DubbingPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

shutdown_requested = False


def handle_signal(signum, frame):
    global shutdown_requested
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown_requested = True


def run_worker():
    """
    Redis-based queue worker that processes dubbing jobs sequentially.
    Segments within each job are processed one at a time to prevent overlap.
    """
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logger.info("Starting dubbing queue worker...")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    logger.info(f"Connected to Redis at {REDIS_URL}")
    logger.info("Waiting for dubbing jobs...")

    while not shutdown_requested:
        try:
            result = redis_client.brpop("dubbing_queue", timeout=5)
            if result is None:
                continue

            _, job_id = result
            logger.info(f"Processing job: {job_id}")

            job_data = redis_client.hgetall(f"job:{job_id}")
            if not job_data:
                logger.error(f"Job {job_id} not found in Redis")
                continue

            video_path = job_data.get("source_video", "")
            target_language = job_data.get("target_language", "en")
            source_language = job_data.get("source_language", "auto")

            if not video_path:
                logger.error(f"Job {job_id} has no source video")
                redis_client.hset(
                    f"job:{job_id}",
                    mapping={
                        "status": "failed",
                        "error": "No source video specified",
                    },
                )
                continue

            pipeline = DubbingPipeline(redis_client, job_id)
            pipeline.run(video_path, target_language, source_language)

        except Exception as e:
            logger.error(f"Worker error processing job: {e}", exc_info=True)
            if job_id:
                redis_client.hset(
                    f"job:{job_id}",
                    mapping={
                        "status": "failed",
                        "error": str(e),
                    },
                )
            time.sleep(1)

    logger.info("Worker shutdown complete")


if __name__ == "__main__":
    run_worker()
