
import json
import os
import requests
from botchan.audio.speech_to_text.base import SpeechToText
from botchan.audio.speech_to_text.data_model import (
    WhisperXResponse,
)
from botchan.logger import get_logger
from botchan.utt.singleton import Singleton
from botchan.utt.timed import timed

logger = get_logger(__name__)

# Whisper use a shorter version for language code. Provide a mapping to convert
# from the standard language code to the whisper language code.
WHISPER_LANGUAGE_CODE_MAPPING = {
    "en-US": "en",
    "es-ES": "es",
    "fr-FR": "fr",
    "de-DE": "de",
    "it-IT": "it",
    "pt-PT": "pt",
    "hi-IN": "hi",
    "pl-PL": "pl",
    "zh-CN": "zh",
    "ja-JP": "jp",
    "ko-KR": "ko",
}


DIARIZATION = os.getenv("JOURNAL_MODE", "false").lower() == "true"
WHISPER_X_API_KEY = os.getenv("WHISPER_X_API_KEY", "")
WHISPER_X_API_URL = os.getenv("WHISPER_X_API_URL", "")
WHISPER_X_API_URL_JOURNAL = os.getenv("WHISPER_X_API_URL_JOURNAL", "")


class WhisperX(Singleton, SpeechToText):
    def __init__(self):
        super().__init__()

    @timed
    def transcribe(
        self, audio_bytes, prompt="", language="", suppress_tokens=[-1]
    ):
        logger.info("Transcribing audio...")
        result = self._transcribe_api(
            audio_bytes, prompt, language, suppress_tokens
        )
        if isinstance(result, dict):
            segments = result.get("segments", [])
            text = " ".join([seg.get("text", "").strip() for seg in segments])
            return text
        else:
            return ""

    def _transcribe_api(
        self,
        audio_bytes,
        prompt="",
        language="",
        suppress_tokens=[-1],
        diarization=False,
        speaker_audio_samples={},
    ):
        files = {"audio_file": ("", audio_bytes)}
        for id, speaker_audio_sample in speaker_audio_samples.items():
            files[f"speaker_audio_sample_{id}"] = ("", speaker_audio_sample)
        metadata = {
            "api_key": WHISPER_X_API_KEY,
            "platform": "web",
            "initial_prompt": prompt,
            "language": language,
            "suppress_tokens": suppress_tokens,
            "diarization": diarization,
        }
        data = {"metadata": json.dumps(metadata)}
        url = WHISPER_X_API_URL_JOURNAL if diarization else WHISPER_X_API_URL
        try:
            logger.info(
                f"Sent request to whisperX server {url}: {len(audio_bytes)} bytes"
            )
            response = requests.post(url, data=data, files=files)
            return WhisperXResponse(**response.json())
        except requests.exceptions.Timeout as e:
            logger.error(f"WhisperX server {url} timed out: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not connect to whisperX server {url}: {e}")
        except KeyError as e:
            logger.error(f"Could not parse response from whisperX server {url}: {e}")
        except Exception as e:
            logger.error(f"Unknown error from whisperX server {url}: {e}")
