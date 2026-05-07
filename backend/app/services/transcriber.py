import logging

logger = logging.getLogger(__name__)

_whisper_model = None


def _get_model():
    """Lazy-load Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        import whisper
        from app.config import WHISPER_MODEL

        logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        logger.info("Whisper model loaded")
    return _whisper_model


def transcribe_segment(
    audio_path: str,
    language: str | None = None,
) -> dict:
    """
    Transcribe a single speaker segment using Whisper.
    This processes ONE segment at a time — never the full audio.

    Returns dict with 'text', 'language', and 'segments' (word-level timing).
    """
    model = _get_model()

    options = {
        "task": "transcribe",
        "verbose": False,
    }
    if language and language != "auto":
        options["language"] = language

    logger.info(f"Transcribing segment: {audio_path}")
    result = model.transcribe(audio_path, **options)

    text = result.get("text", "").strip()
    detected_language = result.get("language", language or "en")

    word_segments = []
    for seg in result.get("segments", []):
        word_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })

    logger.info(
        f"Transcription: '{text[:80]}...' (lang={detected_language})"
        if len(text) > 80
        else f"Transcription: '{text}' (lang={detected_language})"
    )

    return {
        "text": text,
        "language": detected_language,
        "segments": word_segments,
    }
