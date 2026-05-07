import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

_diarization_pipeline = None


def _get_pipeline():
    """Lazy-load pyannote diarization pipeline."""
    global _diarization_pipeline
    if _diarization_pipeline is None:
        from pyannote.audio import Pipeline
        from app.config import PYANNOTE_AUTH_TOKEN

        logger.info("Loading pyannote diarization pipeline...")
        _diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=PYANNOTE_AUTH_TOKEN or None,
        )
        logger.info("Diarization pipeline loaded")
    return _diarization_pipeline


def diarize(vocals_path: str) -> list[dict]:
    """
    Run speaker diarization on the vocal track.
    Returns list of segments with speaker_id, start, end times.
    """
    pipeline = _get_pipeline()

    logger.info(f"Running diarization on {vocals_path}")
    diarization = pipeline(vocals_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker_id": speaker,
            "start": round(turn.start, 3),
            "end": round(turn.end, 3),
        })

    segments = _merge_adjacent_segments(segments)
    logger.info(f"Diarization complete: {len(segments)} segments found")
    return segments


def _merge_adjacent_segments(
    segments: list[dict], gap_threshold: float = 0.5
) -> list[dict]:
    """Merge adjacent segments from the same speaker if gap is small."""
    if not segments:
        return segments

    merged = [segments[0].copy()]
    for seg in segments[1:]:
        last = merged[-1]
        if (
            seg["speaker_id"] == last["speaker_id"]
            and (seg["start"] - last["end"]) < gap_threshold
        ):
            last["end"] = seg["end"]
        else:
            merged.append(seg.copy())

    return merged


def detect_gender(audio_path: str) -> str:
    """
    Detect speaker gender from a voice segment using pitch analysis.
    Male voices typically have fundamental frequency < 165 Hz.
    Female voices typically have fundamental frequency > 165 Hz.
    """
    try:
        import librosa

        y, sr = librosa.load(audio_path, sr=16000)
        if len(y) < sr * 0.1:
            return "male"

        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 50:
                pitch_values.append(pitch)

        if not pitch_values:
            return "male"

        median_pitch = float(np.median(pitch_values))
        gender = "female" if median_pitch > 165 else "male"
        logger.info(
            f"Gender detection: median_pitch={median_pitch:.1f}Hz -> {gender}"
        )
        return gender

    except Exception as e:
        logger.warning(f"Gender detection failed, defaulting to male: {e}")
        return "male"
