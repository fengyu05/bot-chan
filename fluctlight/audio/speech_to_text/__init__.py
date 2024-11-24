# pylint: disable=import-outside-toplevel
from fluctlight.audio.speech_to_text.base import SpeechToText
from fluctlight.settings import SPEECH_TO_TEXT_ENGINE

def get_speech_to_text(use: str = SPEECH_TO_TEXT_ENGINE) -> SpeechToText:
    if use == "GOOGLE":
        from fluctlight.audio.speech_to_text.google import Google
        Google.initialize()
        return Google.get_instance()
    elif use == "OPENAI_WHISPER":
        from fluctlight.audio.speech_to_text.whisper import Whisper
        Whisper.initialize()
        return Whisper.get_instance()
    elif use == "WHISPER_X_API":
        from fluctlight.audio.speech_to_text.whisperX import WhisperX
        WhisperX.initialize()
        return WhisperX.get_instance()
    else:
        raise NotImplementedError(f"Unknown speech to text engine: {use}")
