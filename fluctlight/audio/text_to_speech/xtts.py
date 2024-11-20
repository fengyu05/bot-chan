import asyncio
import base64

import requests
from fastapi import WebSocket

from fluctlight.audio.text_to_speech.base import TextToSpeech
from fluctlight.audio.text_to_speech.utils import MP3ToUlaw
from fluctlight.logger import get_logger
from fluctlight.settings import XTTS_API_KEY, XTTS_API_URL
from fluctlight.utt.singleton import Singleton
from fluctlight.utt.timed import timed

logger = get_logger(__name__)


class XTTS(Singleton, TextToSpeech):
    def __init__(self):
        super().__init__()
        logger.info("Initializing [XTTS Text To Speech] voices...")

    @timed
    async def stream(
        self,
        text: str,
        websocket: WebSocket,
        tts_event: asyncio.Event,
        voice_id: str = "default",
        first_sentence: bool = False,
        language: str = "",
        sid: str = "",
        platform: str = "",
        priority: int = 100,  # 0 is highest priority
        *args,
        **kwargs,
    ) -> None:
        if voice_id == "":
            logger.info("XTTS voice_id is not set, using default voice")
            voice_id = "default"
        headers = {"api-key": XTTS_API_KEY}
        data = {
            "prompt": text,
            "language": language,
            "voice_id": voice_id,
            "max_ref_length": 30,
            "gpt_cond_len": 6,
            "gpt_cond_chunk_len": 4,
            "speed": 1.2,
            "temperature": 0.01,
            "stream": first_sentence,
            "priority": priority,
        }
        with requests.post(
            XTTS_API_URL, json=data, headers=headers, stream=True
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=None):
                if not chunk:
                    continue
                if tts_event.is_set():
                    # stop streaming audio
                    break
                if platform != "twilio":
                    await websocket.send_bytes(chunk)
                    await asyncio.sleep(
                        0.001
                    )  # don't remove! this avoids sending in a batch
                else:
                    audio_bytes = MP3ToUlaw(chunk)
                    audio_b64 = base64.b64encode(audio_bytes).decode()
                    media_response = {
                        "event": "media",
                        "streamSid": sid,
                        "media": {
                            "payload": audio_b64,
                        },
                    }
                    # "done" marker is sent to twilio to track if the audio has been completed.
                    await websocket.send_json(media_response)
                    mark = {
                        "event": "mark",
                        "streamSid": sid,
                        "mark": {
                            "name": "done",
                        },
                    }
                    await websocket.send_json(mark)
