import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_tts_engine = None


def _get_tts():
    """Lazy-load Coqui TTS engine."""
    global _tts_engine
    if _tts_engine is None:
        from TTS.api import TTS

        logger.info("Loading Coqui TTS engine...")
        _tts_engine = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        logger.info("Coqui TTS engine loaded")
    return _tts_engine


def generate_speech(
    text: str,
    output_path: str,
    gender: str = "male",
    target_language: str = "en",
    reference_audio: str | None = None,
    target_duration: float | None = None,
) -> str:
    """
    Generate TTS audio for a single segment using Coqui TTS.
    Uses gender-appropriate voice and matches duration to original segment.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    tts = _get_tts()

    speaker_wav = reference_audio
    if not speaker_wav:
        speaker_wav = _get_default_speaker(gender)

    logger.info(
        f"Generating TTS: text='{text[:50]}...', gender={gender}, "
        f"lang={target_language}"
    )

    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speaker_wav=speaker_wav,
        language=target_language,
    )

    if target_duration and target_duration > 0:
        output_path = _adjust_duration(output_path, target_duration)

    logger.info(f"TTS audio generated: {output_path}")
    return output_path


def _get_default_speaker(gender: str) -> str | None:
    """Get default speaker reference audio based on gender."""
    base_dir = Path(__file__).resolve().parent.parent.parent / "speaker_refs"
    base_dir.mkdir(parents=True, exist_ok=True)

    male_ref = base_dir / "male_reference.wav"
    female_ref = base_dir / "female_reference.wav"

    if gender == "female" and female_ref.exists():
        return str(female_ref)
    elif male_ref.exists():
        return str(male_ref)

    return None


def _adjust_duration(audio_path: str, target_duration: float) -> str:
    """
    Time-stretch or compress audio to match the target duration.
    Uses FFmpeg's atempo filter.
    """
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning("Could not probe audio duration, skipping adjustment")
        return audio_path

    current_duration = float(result.stdout.strip())
    if current_duration <= 0:
        return audio_path

    tempo = current_duration / target_duration

    tempo = max(0.5, min(tempo, 2.0))

    if abs(tempo - 1.0) < 0.05:
        return audio_path

    adjusted_path = audio_path.replace(".wav", "_adjusted.wav")

    atempo_filters = []
    remaining = tempo
    while remaining > 2.0:
        atempo_filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        atempo_filters.append("atempo=0.5")
        remaining /= 0.5
    atempo_filters.append(f"atempo={remaining:.4f}")

    filter_str = ",".join(atempo_filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter:a", filter_str,
        adjusted_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"Duration adjustment failed: {result.stderr}")
        return audio_path

    logger.info(
        f"Adjusted duration: {current_duration:.2f}s -> {target_duration:.2f}s "
        f"(tempo={tempo:.2f})"
    )
    return adjusted_path


def get_audio_duration(audio_path: str) -> float:
    """Get audio file duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0
    return float(result.stdout.strip())
