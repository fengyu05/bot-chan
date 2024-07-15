from collections import OrderedDict
from typing import Any

import structlog

import botchan.agents.prompt_bank as prompt_bank
from botchan.agents.openai_whisper_agent import OpenAiWhisperAgent
from botchan.openai import CLIENT as client
from botchan.openai.chat_utils import get_message_from_response
from botchan.openai.common import VISION_INPUT_SUPPORT_TYPE
from botchan.settings import OPENAI_GPT_MODEL_ID
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.utt.files import base64_encode_slack_image, download_slack_downloadable

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
        self.whisper_agent = OpenAiWhisperAgent()

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
            content_from_files = self.process_files(message_event)
            content.extend(content_from_files)

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

    def process_files(self, message_event: MessageEvent) -> list[dict]:
        """
        Process data by examining each file and determining its type.
        """
        data = []

        for file_object in message_event.files:
            if self._accept_image_filetype(file_object):
                base64_image = base64_encode_slack_image(
                    file_object.url_private_download
                )
                data.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low",
                        },
                    }
                )
            elif self._accept_slack_audio(file_object):
                local_audio_file = download_slack_downloadable(file_object.aac)
                data.append(
                    {
                        "type": "text",
                        "text": self.whisper_agent.transcribe(local_audio_file),
                    }
                )
        return data

    def _accept_image_filetype(self, file_object: FileObject) -> bool:
        return file_object.filetype.lower() in VISION_INPUT_SUPPORT_TYPE

    def _accept_slack_audio(self, file_object: FileObject) -> bool:
        return file_object.subtype == "slack_audio"
