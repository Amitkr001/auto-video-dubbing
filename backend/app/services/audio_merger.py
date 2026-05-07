import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def merge_dubbed_segments(
    segments: list[dict],
    total_duration: float,
    output_path: str,
) -> str:
    """
    Rebuild the full dubbed vocal track by placing TTS segments
    at their exact original timestamps.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    silence_path = output_path.replace(".wav", "_silence.wav")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=16000:cl=mono:d={total_duration}",
        "-acodec", "pcm_s16le",
        silence_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create silence track: {result.stderr}")

    current_track = silence_path

    for i, segment in enumerate(segments):
        tts_path = segment.get("tts_audio_path", "")
        if not tts_path or not Path(tts_path).exists():
            logger.warning(f"Segment {i} has no TTS audio, skipping")
            continue

        start_time = segment["start"]
        temp_output = output_path.replace(".wav", f"_merge_{i}.wav")

        delay_ms = int(start_time * 1000)
        cmd = [
            "ffmpeg", "-y",
            "-i", current_track,
            "-i", tts_path,
            "-filter_complex",
            f"[1:a]adelay={delay_ms}|{delay_ms}[delayed];"
            f"[0:a][delayed]amix=inputs=2:duration=first:dropout_transition=0",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            temp_output,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to merge segment {i}: {result.stderr}")
            continue

        if current_track != silence_path:
            Path(current_track).unlink(missing_ok=True)
        current_track = temp_output

    if current_track != output_path:
        Path(current_track).rename(output_path)

    Path(silence_path).unlink(missing_ok=True)

    logger.info(f"Dubbed vocal track rebuilt: {output_path}")
    return output_path


def merge_vocals_with_background(
    dubbed_vocals_path: str,
    background_path: str,
    output_path: str,
) -> str:
    """
    Merge the dubbed vocal track with the original background music/ambient.
    Background is preserved from the original; dubbed vocals replace originals.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", dubbed_vocals_path,
        "-i", background_path,
        "-filter_complex",
        "[0:a]volume=1.0[vocals];"
        "[1:a]volume=0.8[bg];"
        "[vocals][bg]amix=inputs=2:duration=longest:dropout_transition=2",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Vocals + background merge failed: {result.stderr}"
        )

    logger.info(f"Merged dubbed vocals with background: {output_path}")
    return output_path


def replace_audio_in_video(
    video_path: str,
    audio_path: str,
    output_path: str,
) -> str:
    """
    Replace original audio in video with dubbed audio using FFmpeg.
    Video stream is copied without re-encoding to preserve quality.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Audio replacement in video failed: {result.stderr}"
        )

    logger.info(f"Final dubbed video: {output_path}")
    return output_path


def get_media_duration(file_path: str) -> float:
    """Get duration of audio or video file in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0
    return float(result.stdout.strip())
