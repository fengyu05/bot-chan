# pylint: disable=import-outside-toplevel
import os

from botchan.audio.text_to_speech.base import TextToSpeech
from botchan.settings import TTS_ENGINE

tts_env_vars = {
    "ELEVEN_LABS": "ELEVEN_LABS_API_KEY",
    "GOOGLE_TTS": "GOOGLE_APPLICATION_CREDENTIALS",
    "XTTS": "XTTS_API_KEY",
}


def get_text_to_speech(tts: str | None = None) -> TextToSpeech:
    if not tts:
        tts = TTS_ENGINE
    if tts in tts_env_vars and not os.getenv(tts_env_vars[tts]):
        assert False, "TTS engine misconfigured"

    if tts == "ELEVEN_LABS":
        from botchan.audio.text_to_speech.elevenlabs import ElevenLabs

        ElevenLabs.initialize()
        return ElevenLabs.get_instance()
    elif tts == "GOOGLE_TTS":
        from botchan.audio.text_to_speech.google_cloud_tts import GoogleCloudTTS

        GoogleCloudTTS.initialize()
        return GoogleCloudTTS.get_instance()
    elif tts == "XTTS":
        from botchan.audio.text_to_speech.xtts import XTTS

        XTTS.initialize()
        return XTTS.get_instance()
    else:
        raise NotImplementedError(f"Unknown text to speech engine: {tts}")
