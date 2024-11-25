import io

import speech_recognition as sr
from pydub import AudioSegment

from fluctlight.audio.speech_to_text.base import SpeechToText
from fluctlight.audio.speech_to_text.data_model import AudioFormat
from fluctlight.logger import get_logger
from fluctlight.settings import OPENAI_API_KEY
from fluctlight.utt.singleton import Singleton

logger = get_logger(__name__)


class Whisper(Singleton, SpeechToText):
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()

    def transcribe(  # pylint: disable=W0221:arguments-differ
        self, audio_bytes: bytes, platform: AudioFormat = AudioFormat.WAV
    ) -> str:
        logger.info("Transcribing audio...", audio_bytes=len(audio_bytes))
        return self.recognizer.recognize_whisper_api(
            audio_bytes,
            api_key=OPENAI_API_KEY,
        )

    def _convert_webm_to_wav(self, webm_data):
        webm_audio = AudioSegment.from_file(io.BytesIO(webm_data))
        wav_data = io.BytesIO()
        webm_audio.export(wav_data, format="wav")
        with sr.AudioFile(wav_data) as source:
            audio = self.recognizer.record(source)
        return audio

    def _convert_bytes_to_wav(self, audio_bytes):
        return sr.AudioData(audio_bytes, 44100, 2)

    def _ulaw_to_wav(self, audio_bytes):
        sound = AudioSegment(
            data=audio_bytes, sample_width=1, frame_rate=8000, channels=1
        )
        audio = io.BytesIO()
        sound.export(audio, format="wav")
        return sr.AudioData(audio_bytes, 8000, 1)
