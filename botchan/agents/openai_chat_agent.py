from typing import Optional
from enum import Enum

import structlog
import botchan.agents.prompt_bank as prompt_bank
from botchan.openai.files import upload_from_url
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.settings import OPENAI_GPT_MODEL_ID, BOT_NAME
from botchan.utt.files import base64_encode_slack_image
from botchan.openai import CLIENT as client
from botchan.openai.chat_utils import get_message_from_response

logger = structlog.getLogger(__name__)


class OpenAiChatAgent:
    def __init__(self) -> None:
        pass

    def qa(self, message_event: MessageEvent) -> str:
        """
        Process a message event and return a response.

        This method processes the message event, handling both text and image data
        if present, and integrates it into the HumanMessage content before invoking
        the chain to generate a response.

        Args:
            message_event (MessageEvent): The message event to process, which may
                                        contain both text and image data.

        Returns:
            str: The generated response.
        """
        logger.debug("chat agent qa invoke with image", text=message_event.text)

        content = [{"type": "text", "text": message_event.text}]
        if message_event.has_files:
            images_data = self._process_image(message_event)
            content.extend(images_data)

        response = client.chat.completions.create(
            model=OPENAI_GPT_MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )
        logger.info("qa get response", response=response)
        return get_message_from_response(response)

    def _process_image(self, message_event: MessageEvent) -> list[dict]:
        files = [
            file_object
            for file_object in message_event.files
            if self._accept_image_filetype(file_object)
        ]
        data = []
        for f in files:
            base64_image = base64_encode_slack_image(f.url_private_download)
            data.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "low",
                    },
                }
            )

        return data

    def _accept_image_filetype(self, file_object: FileObject) -> bool:
        return file_object.filetype.lower() in ("png", "jpg", "jpeg", "gif")
