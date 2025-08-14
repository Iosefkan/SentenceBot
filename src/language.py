from typing import Optional

from deep_translator import GoogleTranslator

from config import SUPPORTED_LANGUAGES


def normalize_lang_code(user_code: str) -> Optional[str]:
    code = (user_code or "").strip().lower()
    return code if code in SUPPORTED_LANGUAGES else None


def translate(text: str, target_code: str) -> str:
    cfg = SUPPORTED_LANGUAGES[target_code]
    translator = GoogleTranslator(source="auto", target=cfg["translator_code"])
    return translator.translate(text)


