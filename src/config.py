import logging
import os
from typing import Dict

from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("english-sentences-bot")


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is missing. Create a .env file with TELEGRAM_BOT_TOKEN=..."
    )

DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")
XTTS_SPEAKER_WAV = os.getenv("XTTS_SPEAKER_WAV", "").strip() or None


SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "translator_code": "en", "tts_code": "en"},
    "es": {"name": "Spanish", "translator_code": "es", "tts_code": "es"},
    "fr": {"name": "French", "translator_code": "fr", "tts_code": "fr"},
    "de": {"name": "German", "translator_code": "de", "tts_code": "de"},
    "it": {"name": "Italian", "translator_code": "it", "tts_code": "it"},
    "pt": {"name": "Portuguese", "translator_code": "pt", "tts_code": "pt"},
    "ru": {"name": "Russian", "translator_code": "ru", "tts_code": "ru"},
    "pl": {"name": "Polish", "translator_code": "pl", "tts_code": "pl"},
    "tr": {"name": "Turkish", "translator_code": "tr", "tts_code": "tr"},
    "nl": {"name": "Dutch", "translator_code": "nl", "tts_code": "nl"},
    "sv": {"name": "Swedish", "translator_code": "sv", "tts_code": "sv"},
    "fi": {"name": "Finnish", "translator_code": "fi", "tts_code": "fi"},
    "da": {"name": "Danish", "translator_code": "da", "tts_code": "da"},
    "no": {"name": "Norwegian", "translator_code": "no", "tts_code": "no"},
    "uk": {"name": "Ukrainian", "translator_code": "uk", "tts_code": "uk"},
    "cs": {"name": "Czech", "translator_code": "cs", "tts_code": "cs"},
    "el": {"name": "Greek", "translator_code": "el", "tts_code": "el"},
    "ro": {"name": "Romanian", "translator_code": "ro", "tts_code": "ro"},
    "hu": {"name": "Hungarian", "translator_code": "hu", "tts_code": "hu"},
    "bg": {"name": "Bulgarian", "translator_code": "bg", "tts_code": "bg"},
    "ar": {"name": "Arabic", "translator_code": "ar", "tts_code": "ar"},
    "he": {"name": "Hebrew", "translator_code": "he", "tts_code": "he"},
    "hi": {"name": "Hindi", "translator_code": "hi", "tts_code": "hi"},
    "ko": {"name": "Korean", "translator_code": "ko", "tts_code": "ko"},
    "ja": {"name": "Japanese", "translator_code": "ja", "tts_code": "ja"},
    "zh": {"name": "Chinese (Simplified)", "translator_code": "zh-CN", "tts_code": "zh-cn"},
}

DEFAULT_SOURCE_LANG = "ru"
DEFAULT_TARGET_LANG = "en"
DEFAULT_DAILY_QUOTA = 5


