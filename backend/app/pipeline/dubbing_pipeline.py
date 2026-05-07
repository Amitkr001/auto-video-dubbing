import json
import logging
from pathlib import Path

import redis

from app.config import TEMP_DIR, OUTPUT_DIR
from app.models import JobStatus
from app.services.audio_separator import (
    extract_audio,
    separate_vocals,
    extract_audio_segment,
    extract_video_segment,
)
from app.services.diarization import diarize, detect_gender
from app.services.transcriber import transcribe_segment
from app.services.translator import translate_text
from app.services.tts_generator import generate_speech
from app.services.lipsync import apply_lipsync
from app.services.audio_merger import (
    merge_dubbed_segments,
    merge_vocals_with_background,
    replace_audio_in_video,
    get_media_duration,
)

logger = logging.getLogger(__name__)


class DubbingPipeline:
    """
    Orchestrates the full dubbing pipeline in strict order:
    1. Extract audio from video (FFmpeg)
    2. Separate vocals from background (Demucs)
    3. Diarize speakers with timestamps (pyannote)
    4. Per segment: transcribe -> detect gender -> translate -> clean text
    5. Per segment: generate TTS with gender-matched voice
    6. Per segment: apply Wav2Lip lip sync
    7. Rebuild dubbed vocal track at exact timestamps
    8. Merge dubbed vocals with background
    9. Replace audio in video without re-encoding video
    """

    def __init__(self, redis_client: redis.Redis, job_id: str):
        self.redis = redis_client
        self.job_id = job_id
        self.job_dir = TEMP_DIR / job_id
        self.job_dir.mkdir(parents=True, exist_ok=True)

    def _update_status(
        self,
        status: JobStatus,
        progress: float,
        stage: str,
        **kwargs,
    ):
        updates = {
            "status": status.value,
            "progress": progress,
            "current_stage": stage,
        }
        updates.update(kwargs)
        self.redis.hset(f"job:{self.job_id}", mapping=updates)
        logger.info(f"[{self.job_id}] {stage} ({progress:.0%})")

    def run(self, video_path: str, target_language: str, source_language: str = "auto"):
        """Execute the full dubbing pipeline."""
        try:
            # ── Step 1: Extract audio from video ──
            self._update_status(
                JobStatus.EXTRACTING, 0.05, "Extracting audio from video"
            )
            audio_path = extract_audio(video_path, self.job_id)
            total_duration = get_media_duration(audio_path)

            # ── Step 2: Separate vocals and background ──
            self._update_status(
                JobStatus.SEPARATING, 0.10, "Separating vocals and background"
            )
            separated = separate_vocals(audio_path, self.job_id)
            vocals_path = separated["vocals"]
            background_path = separated["background"]

            # ── Step 3: Speaker diarization ──
            self._update_status(
                JobStatus.DIARIZING, 0.20, "Detecting speakers"
            )
            raw_segments = diarize(vocals_path)
            total_segments = len(raw_segments)
            self._update_status(
                JobStatus.DIARIZING,
                0.25,
                f"Found {total_segments} speaker segments",
                total_segments=total_segments,
            )

            # ── Step 4: Per-segment transcription, gender detection, translation ──
            segments_dir = self.job_dir / "segments"
            segments_dir.mkdir(parents=True, exist_ok=True)

            processed_segments = []
            for i, seg in enumerate(raw_segments):
                seg_progress_base = 0.25 + (i / total_segments) * 0.25

                # 4a. Extract audio segment
                seg_audio = str(segments_dir / f"seg_{i}_audio.wav")
                extract_audio_segment(
                    vocals_path, seg["start"], seg["end"], seg_audio
                )

                # 4b. Transcribe segment
                self._update_status(
                    JobStatus.TRANSCRIBING,
                    seg_progress_base,
                    f"Transcribing segment {i + 1}/{total_segments}",
                    processed_segments=i,
                )
                transcription = transcribe_segment(
                    seg_audio,
                    language=source_language if source_language != "auto" else None,
                )

                if not transcription["text"]:
                    logger.info(f"Segment {i} has no speech, skipping")
                    continue

                detected_lang = transcription["language"]
                if source_language == "auto":
                    source_language = detected_lang

                # 4c. Detect gender
                gender = detect_gender(seg_audio)

                # 4d. Translate text
                self._update_status(
                    JobStatus.TRANSLATING,
                    seg_progress_base + 0.05,
                    f"Translating segment {i + 1}/{total_segments}",
                    processed_segments=i,
                )
                translated = translate_text(
                    transcription["text"],
                    source_language=detected_lang,
                    target_language=target_language,
                )

                seg_data = {
                    "index": i,
                    "speaker_id": seg["speaker_id"],
                    "start": seg["start"],
                    "end": seg["end"],
                    "gender": gender,
                    "original_text": transcription["text"],
                    "translated_text": translated,
                    "seg_audio_path": seg_audio,
                }
                processed_segments.append(seg_data)

            # ── Step 5: Per-segment TTS generation ──
            for i, seg in enumerate(processed_segments):
                seg_progress = 0.50 + (i / len(processed_segments)) * 0.15
                self._update_status(
                    JobStatus.GENERATING_VOICE,
                    seg_progress,
                    f"Generating voice for segment {i + 1}/{len(processed_segments)}",
                    processed_segments=i,
                )

                tts_output = str(segments_dir / f"seg_{seg['index']}_tts.wav")
                segment_duration = seg["end"] - seg["start"]

                tts_path = generate_speech(
                    text=seg["translated_text"],
                    output_path=tts_output,
                    gender=seg["gender"],
                    target_language=target_language,
                    reference_audio=seg["seg_audio_path"],
                    target_duration=segment_duration,
                )
                seg["tts_audio_path"] = tts_path

            # ── Step 6: Per-segment Wav2Lip lip sync ──
            for i, seg in enumerate(processed_segments):
                seg_progress = 0.65 + (i / len(processed_segments)) * 0.15
                self._update_status(
                    JobStatus.LIP_SYNCING,
                    seg_progress,
                    f"Applying lip sync to segment {i + 1}/{len(processed_segments)}",
                    processed_segments=i,
                )

                video_seg_path = str(
                    segments_dir / f"seg_{seg['index']}_video.mp4"
                )
                extract_video_segment(
                    video_path, seg["start"], seg["end"], video_seg_path
                )

                lipsync_output = str(
                    segments_dir / f"seg_{seg['index']}_lipsync.mp4"
                )
                lipsync_path = apply_lipsync(
                    video_seg_path, seg["tts_audio_path"], lipsync_output
                )
                seg["lipsync_video_path"] = lipsync_path

            # ── Step 7: Rebuild full dubbed vocal track ──
            self._update_status(
                JobStatus.MERGING, 0.80, "Rebuilding dubbed vocal track"
            )
            dubbed_vocals_path = str(self.job_dir / "dubbed_vocals.wav")
            merge_dubbed_segments(
                processed_segments, total_duration, dubbed_vocals_path
            )

            # ── Step 8: Merge dubbed vocals with background ──
            self._update_status(
                JobStatus.MERGING,
                0.88,
                "Merging dubbed vocals with background",
            )
            final_audio_path = str(self.job_dir / "final_audio.wav")
            merge_vocals_with_background(
                dubbed_vocals_path, background_path, final_audio_path
            )

            # ── Step 9: Replace audio in video ──
            self._update_status(
                JobStatus.MERGING, 0.95, "Replacing audio in video"
            )
            output_video = str(
                OUTPUT_DIR / f"dubbed_{self.job_id}.mp4"
            )
            replace_audio_in_video(video_path, final_audio_path, output_video)

            # ── Done ──
            self._update_status(
                JobStatus.COMPLETED,
                1.0,
                "Dubbing complete",
                output_video=output_video,
                processed_segments=len(processed_segments),
            )
            logger.info(f"[{self.job_id}] Pipeline complete: {output_video}")

        except Exception as e:
            logger.error(f"[{self.job_id}] Pipeline failed: {e}", exc_info=True)
            self._update_status(
                JobStatus.FAILED, 0.0, "Failed", error=str(e)
            )
            raise
