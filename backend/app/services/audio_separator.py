import subprocess
import logging
from pathlib import Path

from app.config import TEMP_DIR

logger = logging.getLogger(__name__)


def extract_audio(video_path: str, job_id: str) -> str:
    """Extract audio from video using FFmpeg."""
    output_path = str(TEMP_DIR / job_id / "original_audio.wav")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

    logger.info(f"Extracting audio: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")

    logger.info(f"Audio extracted to {output_path}")
    return output_path


def separate_vocals(audio_path: str, job_id: str) -> dict[str, str]:
    """
    Use Demucs to separate vocals from background music/ambient sounds.
    Returns dict with 'vocals' and 'background' paths.
    """
    output_dir = str(TEMP_DIR / job_id / "separated")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "-m", "demucs",
        "--two-stems", "vocals",
        "-o", output_dir,
        "--filename", "{stem}.{ext}",
        audio_path,
    ]

    logger.info(f"Separating vocals with Demucs: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Demucs separation failed: {result.stderr}")

    model_name = "htdemucs"
    vocals_path = str(Path(output_dir) / model_name / "vocals.wav")
    background_path = str(Path(output_dir) / model_name / "no_vocals.wav")

    if not Path(vocals_path).exists():
        possible_dirs = list(Path(output_dir).iterdir())
        if possible_dirs:
            model_dir = possible_dirs[0]
            vocals_path = str(model_dir / "vocals.wav")
            background_path = str(model_dir / "no_vocals.wav")

    if not Path(vocals_path).exists():
        raise RuntimeError(f"Vocals file not found at {vocals_path}")

    logger.info(f"Vocals: {vocals_path}, Background: {background_path}")
    return {
        "vocals": vocals_path,
        "background": background_path,
    }


def extract_video_segment(
    video_path: str, start: float, end: float, output_path: str
) -> str:
    """Extract a video segment between start and end timestamps."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-ss", str(start),
        "-t", str(duration),
        "-c:v", "libx264",
        "-an",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Video segment extraction failed: {result.stderr}")

    return output_path


def extract_audio_segment(
    audio_path: str, start: float, end: float, output_path: str
) -> str:
    """Extract an audio segment between start and end timestamps."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-ss", str(start),
        "-t", str(duration),
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio segment extraction failed: {result.stderr}")

    return output_path
