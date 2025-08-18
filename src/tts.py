import os
import random
import tempfile
from pydub import AudioSegment

from config import SUPPORTED_LANGUAGES, XTTS_SPEAKER_WAV, logger

_tts_model = None
_tts_device = "cpu"


def init_tts():
    global _tts_model, _tts_device
    if _tts_model is not None:
        return
    import torch  # local import to avoid heavy import when not used
    from TTS.api import TTS as CoquiTTS

    _tts_device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    logger.info("Loading TTS model %s on %s (first run may download weights)...", model_name, _tts_device)
    _tts_model = CoquiTTS(model_name).to(_tts_device)


def synthesize_to_wav(text: str, lang_code: str) -> str:
    init_tts()
    tts_lang = SUPPORTED_LANGUAGES[lang_code]["tts_code"]
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_path = tmp.name
    tmp.close()
    try:
        if XTTS_SPEAKER_WAV and os.path.isfile(XTTS_SPEAKER_WAV):
            _tts_model.tts_to_file(text=text, language=tts_lang, speaker_wav=XTTS_SPEAKER_WAV, file_path=tmp_path)
        else:
            if _tts_model.speakers:
                default_speaker_id = random.choice(_tts_model.speakers)
                _tts_model.tts_to_file(text=text, language=tts_lang, speaker=default_speaker_id, file_path=tmp_path)
            else:
                raise ValueError("No speaker_wav provided and no default speaker_id available.")
    except Exception as e:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise e
    return tmp_path

def convert_to_mp3(path) -> str:
    new_path = path[0:-4] + ".mp3"
    try:
        sound = AudioSegment.from_wav(path)
        
        sound = sound.set_frame_rate(44100)
        sound = sound.set_channels(2)
        sound = sound.set_sample_width(2)
        
        sound.export(new_path, format="mp3", bitrate="192k")
        
        os.remove(path)
    except Exception as e:
        try:
            os.remove(new_path)
            os.remove(path)
        except Exception:
            pass
        raise e
    return new_path
