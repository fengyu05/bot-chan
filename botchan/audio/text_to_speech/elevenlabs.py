import asyncio
import base64
import types

import httpx
from fastapi import WebSocket

from botchan.audio.text_to_speech.base import LANG_US, TextToSpeech
from botchan.logger import get_logger
from botchan.settings import ELEVEN_LABS_API_KEY
from botchan.utt.singleton import Singleton
from botchan.utt.timed import timed

logger = get_logger(__name__)

ELEVEN_LABS_MULTILINGUAL_MODEL = "eleven_multilingual_v2"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
DEFAULT_TIMEOUT_SEC = 10

config = types.SimpleNamespace(
    **{
        "chunk_size": 1024,
        "url": "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
        "headers": {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_LABS_API_KEY,
        },
        "data": {
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
    }
)


class ElevenLabs(Singleton, TextToSpeech):
    def __init__(self):
        super().__init__()
        logger.info("Initializing [ElevenLabs Text To Speech] voices...")

    @timed
    async def stream(
        self,
        text: str,
        websocket: WebSocket,
        tts_event: asyncio.Event,
        *args,
        voice_id: str = "",
        first_sentence: bool = False,
        language: str = LANG_US,
        sid: str = "",
        platform: str = "",
        **kwargs,
    ) -> None:
        if voice_id == "":
            voice_id = DEFAULT_VOICE_ID
        headers = config.headers
        if language != LANG_US:
            config.data["model_id"] = ELEVEN_LABS_MULTILINGUAL_MODEL
        data = {
            "text": text,
            **config.data,
        }
        url = config.url.format(voice_id=voice_id)
        url += "?output_format=" + (
            "ulaw_8000" if platform == "twilio" else "mp3_44100_128"
        )
        if first_sentence:
            url += "&optimize_streaming_latency=4"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            if response.status_code != 200:
                logger.error(f"ElevenLabs returns response {response.status_code}")
            async for chunk in response.aiter_bytes():
                await asyncio.sleep(0.1)
                if tts_event.is_set():
                    # stop streaming audio
                    break
                if platform != "twilio":
                    await websocket.send_bytes(chunk)
                else:
                    audio_b64 = base64.b64encode(chunk).decode()
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

    async def generate_audio(
        self,
        text: str,
        *args,
        voice_id: str = "",
        language: str = LANG_US,
        **kwargs,
    ) -> bytes:
        if voice_id == "":
            voice_id = DEFAULT_VOICE_ID
        headers = config.headers
        if language != LANG_US:
            config.data["model_id"] = ELEVEN_LABS_MULTILINGUAL_MODEL
        data = {
            "text": text,
            **config.data,
        }
        # Change to non-streaming endpoint
        url = config.url.format(voice_id=voice_id).replace("/stream", "")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=data, headers=headers, timeout=DEFAULT_TIMEOUT_SEC
            )
            if response.status_code != 200:
                logger.error("ElevenLabs returns response not OK", response=response)
                raise httpx.NetworkError(
                    f"ElevenLabs call fail, code={response.status_code}"
                )
            # Get audio/mpeg from the response and return it
            else:
                logger.info("ElevenLabs returns response OK", response=response)
            return response.content
