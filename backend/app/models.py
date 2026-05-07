from enum import Enum
from typing import Optional
from pydantic import BaseModel


class JobStatus(str, Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    SEPARATING = "separating"
    DIARIZING = "diarizing"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    GENERATING_VOICE = "generating_voice"
    LIP_SYNCING = "lip_syncing"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


class SpeakerSegment(BaseModel):
    speaker_id: str
    start: float
    end: float
    gender: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    tts_audio_path: Optional[str] = None
    lipsync_video_path: Optional[str] = None


class DubbingJob(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    progress: float = 0.0
    current_stage: str = "Queued"
    source_video: str = ""
    target_language: str = ""
    source_language: Optional[str] = None
    segments: list[SpeakerSegment] = []
    output_video: Optional[str] = None
    error: Optional[str] = None
    total_segments: int = 0
    processed_segments: int = 0


class DubbingRequest(BaseModel):
    target_language: str
    source_language: Optional[str] = "auto"


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float
    current_stage: str
    error: Optional[str] = None
    output_video: Optional[str] = None
    total_segments: int = 0
    processed_segments: int = 0


class LanguageListResponse(BaseModel):
    languages: dict[str, str]
