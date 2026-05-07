import re
import logging

logger = logging.getLogger(__name__)

_tokenizer = None
_model = None


def _get_model():
    """Lazy-load M2M100 translation model."""
    global _tokenizer, _model
    if _model is None:
        from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
        from app.config import M2M100_MODEL

        logger.info(f"Loading M2M100 model: {M2M100_MODEL}")
        _tokenizer = M2M100Tokenizer.from_pretrained(M2M100_MODEL)
        _model = M2M100ForConditionalGeneration.from_pretrained(M2M100_MODEL)
        logger.info("M2M100 model loaded")
    return _tokenizer, _model


LANGUAGE_CODE_MAP = {
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "ru": "ru",
    "zh": "zh",
    "ja": "ja",
    "ko": "ko",
    "ar": "ar",
    "hi": "hi",
    "bn": "bn",
    "ta": "ta",
    "te": "te",
    "tr": "tr",
    "nl": "nl",
    "pl": "pl",
    "sv": "sv",
    "vi": "vi",
}


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
) -> str:
    """
    Translate a single text segment using M2M100.
    This processes ONE segment at a time — never the full script.
    """
    if not text or not text.strip():
        return ""

    if source_language == target_language:
        return text

    tokenizer, model = _get_model()

    src_lang = LANGUAGE_CODE_MAP.get(source_language, source_language)
    tgt_lang = LANGUAGE_CODE_MAP.get(target_language, target_language)

    tokenizer.src_lang = src_lang
    encoded = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    generated_tokens = model.generate(
        **encoded,
        forced_bos_token_id=tokenizer.get_lang_id(tgt_lang),
        max_length=512,
    )

    translated = tokenizer.batch_decode(
        generated_tokens, skip_special_tokens=True
    )[0]

    translated = clean_text_for_tts(translated)

    logger.info(
        f"Translation ({src_lang}->{tgt_lang}): '{text[:50]}' -> '{translated[:50]}'"
    )
    return translated


def clean_text_for_tts(text: str) -> str:
    """Clean translated text for TTS consumption."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^\w\s.,!?;:'\"-]", "", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    return text
