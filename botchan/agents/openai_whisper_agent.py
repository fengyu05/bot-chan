import structlog

from botchan.openai import CLIENT as client

logger = structlog.getLogger(__name__)


class OpenAiWhisperAgent:
    def __init__(self) -> None:
        pass

    def transcribe(self, audio_file_path: str) -> str:
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        logger.info("whisper", audio_file=audio_file_path, transcription=transcription)
        return transcription.text
