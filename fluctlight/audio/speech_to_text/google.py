import types

from google.cloud import speech

from fluctlight.audio.speech_to_text.base import SpeechToText
from fluctlight.logger import get_logger
from fluctlight.utt.singleton import Singleton
from fluctlight.utt.timed import timed

logger = get_logger(__name__)

config = types.SimpleNamespace(
    **{
        "web": {
            "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            "sample_rate_hertz": 48000,
            "language_code": "en-US",
            "max_alternatives": 1,
            "enable_automatic_punctuation": True,
        },
        "terminal": {
            "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
            "sample_rate_hertz": 44100,
            "language_code": "en-US",
            "max_alternatives": 1,
            "enable_automatic_punctuation": True,
        },
        "twilio": {
            "encoding": speech.RecognitionConfig.AudioEncoding.MULAW,
            "sample_rate_hertz": 8000,
            "language_code": "en-uS",
        },
    }
)


class Google(Singleton, SpeechToText):
    def __init__(self):
        super().__init__()
        logger.info("Setting up [Google Speech to Text]...")
        self.client = speech.SpeechClient()

    @timed
    def transcribe(
        self, audio_bytes, platform, prompt="", language="en-US", suppress_tokens=[-1]
    ) -> str:
        batch_config = speech.RecognitionConfig(
            {
                "speech_contexts": [speech.SpeechContext(phrases=prompt.split(","))],
                **config.__dict__[platform],
            }
        )
        batch_config.language_code = language
        if language != "en-US":
            batch_config.alternative_language_codes = ["en-US"]
        response = self.client.recognize(
            config=batch_config, audio=speech.RecognitionAudio(content=audio_bytes)
        )
        if not response.results:
            return ""
        result = response.results[0]
        if not result.alternatives:
            return ""
        return result.alternatives[0].transcript
