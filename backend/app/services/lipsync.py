import subprocess
import logging
from pathlib import Path

from app.config import WAV2LIP_CHECKPOINT

logger = logging.getLogger(__name__)


def apply_lipsync(
    video_segment_path: str,
    audio_segment_path: str,
    output_path: str,
) -> str:
    """
    Apply Wav2Lip lip-sync correction to a video segment.
    Processes ONE segment at a time for precise alignment.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not Path(WAV2LIP_CHECKPOINT).exists():
        logger.warning(
            f"Wav2Lip checkpoint not found at {WAV2LIP_CHECKPOINT}. "
            "Skipping lip sync — merging audio directly."
        )
        return _merge_audio_video_fallback(
            video_segment_path, audio_segment_path, output_path
        )

    cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", WAV2LIP_CHECKPOINT,
        "--face", video_segment_path,
        "--audio", audio_segment_path,
        "--outfile", output_path,
        "--resize_factor", "1",
        "--nosmooth",
    ]

    logger.info(f"Applying Wav2Lip lip sync to segment")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.warning(
            f"Wav2Lip failed: {result.stderr}. Falling back to direct merge."
        )
        return _merge_audio_video_fallback(
            video_segment_path, audio_segment_path, output_path
        )

    logger.info(f"Lip sync applied: {output_path}")
    return output_path


def _merge_audio_video_fallback(
    video_path: str,
    audio_path: str,
    output_path: str,
) -> str:
    """Fallback: merge audio and video without lip sync."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio-video merge failed: {result.stderr}")

    return output_path
