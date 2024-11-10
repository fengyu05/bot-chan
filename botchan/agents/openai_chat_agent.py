from collections import OrderedDict
from typing import Any, Callable

from langsmith import traceable
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

import botchan.agents.prompt_bank as prompt_bank
from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.data_model.interface import IAttachment, IMessage
from botchan.intent.message_intent import create_intent
from botchan.logger import get_logger
from botchan.open import OPENAI_CLIENT
from botchan.open.chat_utils import get_message_from_completion
from botchan.open.common import VISION_INPUT_SUPPORT_TYPE
from botchan.settings import (
    OPENAI_GPT_MODEL_ID,
    SLACK_APP_OAUTH_TOKENS_FOR_WS,
    is_slack_bot,
)
from botchan.utt.files import base64_encode_image

logger = get_logger(__name__)


_AGENT_DESCRIPTION = """ Use this agent to make a natural converastion between the assistant bot and user.

"""

INTENT_KEY = "CHAT"


class OpenAiChatAgent(MessageIntentAgent):
    """
    A Chat Agent using Open chat.completion API.
    Conversation is kept with message_buffer keyed by thread_id, with a max buffer limit of 100
    converation(respect to LRU).
    """

    def __init__(
        self,
        transcribe_slack_audio: Any = None,
        buffer_limit: int = 20,
    ) -> None:
        super().__init__(intent=create_intent(INTENT_KEY))
        self.message_buffer = OrderedDict()
        self.buffer_limit = buffer_limit
        self.transcribe_slack_audio = transcribe_slack_audio

    @property
    def name(self) -> str:
        return "OpenAIChatAgent"

    @property
    def description(self) -> str:
        return _AGENT_DESCRIPTION

    def process_message(self, message: IMessage) -> list[str]:
        """
        Processes a message event and generates a response using an AI model.

        This method handles incoming message events, processes any attached files,
        and generates a response from the AI. It maintains a conversation history
        for each unique thread identified by `thread_id`.
        """
        thread_id = message.thread_message_id

        # Move the accessed thread_id to the end to mark it as recently used
        if thread_id in self.message_buffer:
            self.message_buffer.move_to_end(thread_id)
        else:
            self.message_buffer[thread_id] = [
                {"role": "system", "content": prompt_bank.CONVERSATION_BOT_1}
            ]

        # If the buffer exceeds limit items, remove the oldest one
        if len(self.message_buffer) > self.buffer_limit:
            self.message_buffer.popitem(last=False)

        content = [{"type": "text", "text": message.text}]
        if message.has_attachments:
            content_from_files = self.process_files(message)
            content.extend(content_from_files)

        self.message_buffer[thread_id].append(
            {
                "role": "user",
                "content": content,
            }
        )
        response = self.chat_complete(
            messages=self.message_buffer[thread_id],
        )
        output_text = get_message_from_completion(response)
        self.message_buffer[thread_id].append(
            {
                "role": "assistant",
                "content": output_text,
            }
        )
        return [output_text]

    @traceable(run_type="llm", name="chat_agent")
    def chat_complete(
        self, messages: list[ChatCompletionMessageParam]
    ) -> ChatCompletion:
        return OPENAI_CLIENT.chat.completions.create(
            model=OPENAI_GPT_MODEL_ID,
            messages=messages,
        )

    def process_files(self, message: IMessage) -> list[dict]:
        """
        Process data by examining each file and determining its type.
        """
        data = []
        assert message.attachments, "message_event.files can not be None"
        for attachment in message.attachments:
            if self._accept_vision_content_type(attachment):
                bearer_token = SLACK_APP_OAUTH_TOKENS_FOR_WS if is_slack_bot() else None
                base64_image = base64_encode_image(
                    attachment.url, bearer_token=bearer_token
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
            elif self._accept_slack_audio(attachment):
                data.append(
                    {
                        "type": "text",
                        "text": self.transcribe_slack_audio(
                            channel=message.channel.id, timestamp=message.ts
                        ),
                    }
                )
        return data

    def _accept_vision_content_type(self, attachment: IAttachment) -> bool:
        return attachment.content_type in VISION_INPUT_SUPPORT_TYPE

    def _accept_slack_audio(self, attachment: IAttachment) -> bool:
        if attachment.subtype == "slack_audio":
            if self.transcribe_slack_audio is None:
                logger.warn(
                    "transcribe_slack_audio didn't setup for the agent, ignore the transcribe request"
                )
                return False
            return True
        return False

    def _format_buffer(self, buffer: list[dict[str, Any]]) -> list[str]:
        output = []
        for item in buffer:
            if isinstance(item["content"], str):
                output.append(f'[{item["role"]}]: {item["content"]}')
            elif isinstance(item["content"], list):
                for content_item in item["content"]:
                    if content_item["type"] == "text":
                        output.append(f']{item["role"]}]: {content_item["text"]}')
                    elif content_item["type"] == "image_url":
                        output.append(f'[{item["role"]}]: attach an image')
        return output
