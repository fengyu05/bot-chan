from abc import ABC, abstractmethod
from asyncio import Event

from fastapi import WebSocket

from botchan.utt.timed import timed

LANG_US = "en-US"


class TextToSpeech(ABC):
    @abstractmethod
    @timed
    async def stream(
        self,
        text: str,
        websocket: WebSocket,
        tts_event: Event,
        *args,
        voice_id: str = "",
        first_sentence: bool = False,
        language: str = LANG_US,
        **kwargs,
    ):
        pass

    @abstractmethod
    @timed
    async def generate_audio(
        self,
        text: str,
        *args,
        voice_id: str = "",
        language: str = LANG_US,
        **kwargs,
    ) -> bytes:
        pass
