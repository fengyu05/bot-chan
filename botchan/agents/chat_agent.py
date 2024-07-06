from typing import Optional
from enum import Enum

import structlog
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
)
import botchan.agents.prompt_bank as prompt_bank

from botchan.settings import OPENAI_GPT_MODEL_ID, BOT_NAME

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

    def qa(self, text: str) -> str:
        logger.debug("chat agent qa invoke", text=text)
        response = self.chain.invoke(input=text)
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
            prompt_bank.CONVERSATION_BOT_1
        )
        llm = ChatOpenAI(model_name=OPENAI_GPT_MODEL_ID, temperature=0)
        memory = self._create_buffer_memory(
            memeory_type=memeory_type,
            k=k,
            llm=llm,
        )

        chain = ConversationChain(llm=llm, prompt=prompt_template, memory=memory)

        return chain
