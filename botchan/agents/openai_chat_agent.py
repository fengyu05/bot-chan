from typing import Any
from collections import OrderedDict
import structlog

import botchan.agents.prompt_bank as prompt_bank
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.settings import OPENAI_GPT_MODEL_ID
from botchan.utt.files import base64_encode_slack_image
from botchan.openai import CLIENT as client
from botchan.openai.chat_utils import get_message_from_response
from botchan.openai.common import VISION_INPUT_SUPPORT_TYPE

logger = structlog.getLogger(__name__)


class OpenAiChatAgent:
    """
    A Chat Agent using Open chat.completion API.
    Conversation is kept with message_buffer keyed by thread_id, with a max buffer limit of 100
    converation(respect to LRU).
    """

    def __init__(self, buffer_limit: int = 100) -> None:
        self.message_buffer = OrderedDict()
        self.buffer_limit = buffer_limit

    def qa(self, message_event: MessageEvent) -> str:
        """
        Processes a message event and generates a response using an AI model.

        This method handles incoming message events, processes any attached files,
        and generates a response from the AI. It maintains a conversation history
        for each unique thread identified by `thread_id`.

        Args:
            message_event (MessageEvent): The message event containing text,
                                          thread information, and possible attachments.

        Returns:
            str: The generated response from the AI.
        """
        thread_id = message_event.thread_message_id

        # Move the accessed thread_id to the end to mark it as recently used
        if thread_id in self.message_buffer:
            self.message_buffer.move_to_end(thread_id)
        else:
            self.message_buffer[thread_id] = [
                {"role": "system", "content": prompt_bank.CONVERSATION_BOT_1}
            ]

        # If the buffer exceeds 100 items, remove the oldest one
        if len(self.message_buffer) > self.buffer_limit:
            self.message_buffer.popitem(last=False)

        content = [{"type": "text", "text": message_event.text}]
        if message_event.has_files:
            images_data = self._process_image(message_event)
            content.extend(images_data)

        self.message_buffer[thread_id].append(
            {
                "role": "user",
                "content": content,
            }
        )
        logger.info(
            f"qa with messages for thread {thread_id}",
            messages=self.message_buffer[thread_id],
        )
        response = client.chat.completions.create(
            model=OPENAI_GPT_MODEL_ID,
            messages=self.message_buffer[thread_id],
        )
        logger.info(f"qa get response for thread {thread_id}", response=response)
        output_text = get_message_from_response(response)
        self.message_buffer[thread_id].append(
            {
                "role": "assistant",
                "content": output_text,
            }
        )
        return output_text

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
        return file_object.filetype.lower() in VISION_INPUT_SUPPORT_TYPE
