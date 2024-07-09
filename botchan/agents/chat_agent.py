from typing import Optional
from enum import Enum

import structlog
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.chains import ConversationChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
)
import botchan.agents.prompt_bank as prompt_bank
from botchan.openai.files import upload_from_url
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.settings import OPENAI_GPT_MODEL_ID, BOT_NAME
from botchan.utt.files import base64_encode_slack_image

logger = structlog.getLogger(__name__)


class MemoryType(Enum):
    SIMPLE = "SIMPLE"
    SUMMARY = "SUMMARY"
    WINDOW = "WINDOW"
    WINDOW_SUMMARY = "WINDOW_SUMMARY"


class ChatAgent:
    def __init__(self) -> None:
        self.chain = self._create_conversation_chain(
            memeory_type=MemoryType.WINDOW, k=10
        )

    def qa(self, message_event: MessageEvent) -> str:
        """
        Process a message event and return a response.

        If the message event contains files, it will process the event using the
        `qa_with_image` method. Otherwise, it invokes the chain to generate a response
        based on the text of the message event.

        Args:
            message_event (MessageEvent): The message event to process.

        Returns:
            str: The generated response.
        """
        if message_event.has_files:
            return self.qa_with_image(message_event)

        logger.debug("chat agent qa invoke", text=message_event.text)
        response = self.chain.invoke(input=message_event.text)
        logger.debug("chat response", response=response)
        return response["response"]

    def qa_with_image(self, message_event: MessageEvent) -> str:
        """
        Process a message event containing an image and return a response.

        This method processes the image in the message event and integrates it into
        the HumanMessage content before invoking the chain to generate a response.

        Args:
            message_event (MessageEvent): The message event to process, which contains both
                                          text and image data.

        Returns:
            str: The generated response.
        """
        logger.debug("chat agent qa invoke with image", text=message_event.text)
        images_data = self._process_image(message_event)

        message = HumanMessage(
            content=message_event.text,
            image=images_data[0]
        )
        response = self.chain.invoke([message])
        logger.debug("chat response", response=response)
        return response["response"]

    def _create_buffer_memory(
        self,
        memeory_type: MemoryType,
        k: Optional[int] = None,
        llm: Optional[BaseLanguageModel] = None,
    ) -> ConversationBufferMemory:
        if memeory_type == MemoryType.SIMPLE:
            return ConversationBufferMemory(ai_prefix=BOT_NAME)
        elif memeory_type == MemoryType.SUMMARY:
            if llm is None:
                raise ValueError(
                    "Parameter 'llm' must be provided for SUMMARY memory type"
                )
            return ConversationSummaryMemory(
                llm=llm,
                ai_prefix=BOT_NAME,
            )
        elif memeory_type == MemoryType.WINDOW:
            if k is None:
                raise ValueError(
                    "Parameter 'k' must be provided for WINDOW memory type"
                )
            return ConversationBufferWindowMemory(
                k=k,
                ai_prefix=BOT_NAME,
            )
        elif memeory_type == MemoryType.WINDOW_SUMMARY:
            if llm is None:
                raise ValueError(
                    "Parameter 'llm' must be provided for WINDOW_SUMMARY memory type"
                )
            return ConversationSummaryBufferMemory(
                llm=llm,
                ai_prefix=BOT_NAME,
            )
        else:
            raise ValueError(f"Unknown memory type: {memeory_type}")

    def _create_conversation_chain(
        self, memeory_type: MemoryType, k: Optional[int] = None
    ) -> ConversationChain:
        prompt_template = ChatPromptTemplate.from_template(
            prompt_bank.CONVERSATION_BOT_WITH_FORMATTED_HISTORY_1
        )
        llm = ChatOpenAI(model_name=OPENAI_GPT_MODEL_ID, temperature=0)
        memory = self._create_buffer_memory(
            memeory_type=memeory_type,
            k=k,
            llm=llm,
        )

        chain = ConversationChain(llm=llm, prompt=prompt_template, memory=memory)

        return chain

    def _process_image(self, message_event: MessageEvent) -> list[str]:
        files = [
            file_object
            for file_object in message_event.files
            if self._accept_image_filetype(file_object)
        ]

        #return [base64_encode_slack_image(f.url_private_download) for f in files]
        return [upload_from_url(f.url_private_download, f.name).id for f in files]

    def _accept_image_filetype(self, file_object: FileObject) -> bool:
        return file_object.filetype.lower() in ("png", "jpg", "jpeg", "gif")
