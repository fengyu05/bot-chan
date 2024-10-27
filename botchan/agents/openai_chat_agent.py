import time
from collections import OrderedDict
from typing import Any

import structlog

import botchan.agents.prompt_bank as prompt_bank
from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.intent.message_intent import create_intent
from botchan.open import OPENAI_CLIENT
from botchan.open.chat_utils import get_message_from_completion
from botchan.open.common import VISION_INPUT_SUPPORT_TYPE
from botchan.open.openai_whisper import OpenAiWhisper
from botchan.settings import OPENAI_GPT_MODEL_ID, SLACK_TRANSCRIBE_WAIT_SEC
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.slack.shared import SLACK_MESSAGE_FETCHER
from botchan.utt.files import base64_encode_slack_image, download_slack_downloadable
from botchan.utt.retry import retry

logger = structlog.getLogger(__name__)

_USE_OPENAI_WHISPER = False

_AGENT_DESCRIPTION = """ Use this agent to make a natural converastion between the assistant bot and user.

"""

INTENT_KEY = "CHAT"


class OpenAiChatAgent(MessageIntentAgent):
    """
    A Chat Agent using Open chat.completion API.
    Conversation is kept with message_buffer keyed by thread_id, with a max buffer limit of 100
    converation(respect to LRU).
    """

    def __init__(self, buffer_limit: int = 100) -> None:
        super().__init__(intent=create_intent(INTENT_KEY))
        self.message_buffer = OrderedDict()
        self.buffer_limit = buffer_limit
        self.whisper_agent = OpenAiWhisper()

    @property
    def name(self) -> str:
        return "OpenAIChatAgent"

    @property
    def description(self) -> str:
        return _AGENT_DESCRIPTION

    def process_message(self, message_event: MessageEvent) -> list[str]:
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
            messages=self._format_buffer(self.message_buffer[thread_id]),
        )
        response = OPENAI_CLIENT.chat.completions.create(
            model=OPENAI_GPT_MODEL_ID,
            messages=self.message_buffer[thread_id],
        )
        output_text = get_message_from_completion(response)
        logger.info(
            f"qa get response text for thread {thread_id}", output_text=output_text
        )
        self.message_buffer[thread_id].append(
            {
                "role": "assistant",
                "content": output_text,
            }
        )
        return [output_text]

    def process_files(self, message_event: MessageEvent) -> list[dict]:
        """
        Process data by examining each file and determining its type.
        """
        data = []
        assert message_event.files, "message_event.files can not be None"
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
                text_transcribed = ""

                if _USE_OPENAI_WHISPER:  # Use OpenAI whisper
                    assert file_object.aac
                    local_audio_file = download_slack_downloadable(file_object.aac)
                    text_transcribed = self.whisper_agent.transcribe(local_audio_file)
                else:  # Use Slack transcribe

                    def transcribed_msg_func():
                        time.sleep(SLACK_TRANSCRIBE_WAIT_SEC)
                        transcribed_msg = SLACK_MESSAGE_FETCHER.fetch_message(
                            message_event
                        )
                        logger.debug(
                            "slack transcribed message", transcribed_msg=transcribed_msg
                        )
                        assert transcribed_msg
                        assert isinstance(transcribed_msg.files, list)
                        audio_file = transcribed_msg.files[0]
                        return audio_file.get_transcription_preview()

                    text_transcribed = retry(
                        transcribed_msg_func, retry_time_sec=SLACK_TRANSCRIBE_WAIT_SEC
                    )
                    if not text_transcribed:
                        text_transcribed = "audio not recognizable."
                data.append(
                    {
                        "type": "text",
                        "text": text_transcribed,
                    }
                )
        return data

    def _accept_image_filetype(self, file_object: FileObject) -> bool:
        return file_object.filetype.lower() in VISION_INPUT_SUPPORT_TYPE

    def _accept_slack_audio(self, file_object: FileObject) -> bool:
        return file_object.subtype == "slack_audio"

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
