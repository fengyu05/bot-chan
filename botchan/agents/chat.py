from typing import Optional

import structlog
from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from botchan.message_intent import (
    MessageIntent,
)
from botchan.prompt import Prompt
from botchan.settings import BOT_NAME, OPENAI_GPT_MODEL_ID
from botchan.slack.data_model import Message, MessageEvent
from botchan.slack.messages_fetcher import MessagesFetcher

logger = structlog.getLogger(__name__)


class MultiThreadChatAgent:
    def __init__(self, fetcher: MessagesFetcher, bot_user_id: str) -> None:
        self.llm_chain_pool = {}  # keyed by thread_message_id
        self.bot_user_id = bot_user_id
        self.fetcher = fetcher

    def _new_llm_chain(self, intent: MessageIntent) -> LLMChain:
        prompt = Prompt.from_intent(intent)
        llm_chain = LLMChain(
            llm=OpenAI(
                model_name=OPENAI_GPT_MODEL_ID,
                temperature=0,
            ),
            prompt=PromptTemplate(
                input_variables=prompt.input_variables, template=prompt.template
            ),
            verbose=False,  # Turn this on if we need verbose logs for the prompt
            memory=ConversationBufferWindowMemory(
                k=prompt.memory_buffer,
                input_key=prompt.input_key,  # The key of the input variables that to be kept in memero
            ),
        )
        return llm_chain

    def _get_thread_messages(
        self, message_event: MessageEvent, mentioned_user_id: Optional[str] = None
    ) -> list[Message]:
        assert message_event.thread_ts, "thread_ts can't be non in _get_thread_messages"
        return self.fetcher.fetch(
            channel_id=message_event.channel,
            thread_ts=message_event.thread_ts,
            mentioned_user_id=mentioned_user_id,
        )

    def _get_llm_chain(
        self, message_event: MessageEvent, intent: MessageIntent
    ) -> LLMChain:
        cached_llm_id = f"{message_event.thread_message_id}|{intent.name.lower()}"

        if not cached_llm_id in self.llm_chain_pool:
            chatgpt_chain = self._new_llm_chain(intent)
            self.llm_chain_pool[cached_llm_id] = chatgpt_chain

            # if there is in a thread, load the previous context
            if not message_event.is_thread_root:
                messages = self._get_thread_messages(message_event)
                for message in messages:
                    if (
                        message.ts == message_event.ts
                    ):  # Do not need to reload the current message into memory
                        continue
                    if message.user == message_event.user:
                        chatgpt_chain.memory.chat_memory.add_user_message(message.text)
                    if message.user == self.bot_user_id:
                        chatgpt_chain.memory.chat_memory.add_ai_message(message.text)

        return self.llm_chain_pool[cached_llm_id]

    def run(self, message_event: MessageEvent, message_intent: MessageIntent) -> None:
        chatgpt_chain = self._get_llm_chain(message_event, message_intent)
        return chatgpt_chain.predict(
            human_input=message_event.text, bot_name=BOT_NAME, philosophy_style="modern"
        )
