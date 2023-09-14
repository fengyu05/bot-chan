# pylint: disable=unnecessary-lambda
from typing import Optional

import structlog
from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from slack_sdk import WebClient

from botchan.message_event_handler import MessageEventHandler
from botchan.message_intent import (
    MessageIntent,
    get_message_intent,
    remove_emoji_prefix,
)
from botchan.prompt import Prompt
from botchan.settings import BOT_NAME, OPENAI_GPT_MODEL_ID
from botchan.slack import auth as slack_auth
from botchan.slack import chat as slack_chat
from botchan.slack import reaction as slack_reaction
from botchan.slack.data_model import Message, MessageCreateEvent, MessageEvent
from botchan.slack.messages_fetcher import MessagesFetcher
from botchan.mrkl import create_default_agent
from botchan.buffer_callback import BufferCallbackHandler


logger = structlog.getLogger(__name__)


class Agent:
    llm_chain_pool: dict[str, LLMChain]
    slack_client: WebClient
    fetcher: MessagesFetcher
    bot_user_id: str
    hanlders: list[MessageEventHandler]

    def __init__(self, slack_client: WebClient):
        self.slack_client = slack_client
        self.llm_chain_pool = {}  # keyed by thread_message_id
        self.fetcher = MessagesFetcher(self.slack_client)
        self.bot_user_id = slack_auth.get_bot_user_id(self.slack_client)
        self.mrkl_agent = create_default_agent()

        self.hanlders = [
            # fmt: off
            MessageEventHandler(  ## Handle diaglog chat
                accept_intentions=[MessageIntent.CHAT],
                handler_func=lambda x: self._chat(x),  
            ),
            MessageEventHandler(  ## Handle mrkl agent behaviors
                accept_intentions=[MessageIntent.MRKL_AGENT],
                handler_func=lambda x: self._chain_of_thought(x),
            )
            # fmt: on
        ]

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

    def _should_reply(self, message_event: MessageCreateEvent) -> bool:
        return message_event.channel_type == "im" or message_event.is_user_mentioned(
            self.bot_user_id
        )

    def _thread_mentioned(self, message_event: MessageCreateEvent) -> bool:
        if message_event.thread_ts == None:
            return message_event.is_user_mentioned(self.bot_user_id)
        else:
            messages = self._get_thread_messages(
                message_event, mentioned_user_id=self.bot_user_id
            )
            return len(messages) > 0

    def receive_message(self, message_event: MessageCreateEvent) -> None:
        # IM or mentioned
        if self._should_reply(message_event):
            slack_reaction.add_reaction(
                client=self.slack_client, event=message_event, reaction_name="eyes"
            )
            for handler in self.hanlders:
                handler.handle(message_event)

    def _chat(self, message_event: MessageEvent) -> None:
        chatgpt_chain = self._get_llm_chain(
            message_event, get_message_intent(message=message_event)
        )
        output = chatgpt_chain.predict(
            human_input=message_event.text, bot_name=BOT_NAME, philosophy_style="modern"
        )
        slack_chat.reply_to_message(self.slack_client, message_event, output)

    def _chain_of_thought(self, message_event: MessageEvent) -> None:
        text_buffer = BufferCallbackHandler()
        result = self.mrkl_agent.run(
            remove_emoji_prefix(message_event.text), callbacks=[text_buffer]
        )
        tool_names = ",".join(map(lambda x: x.name, self.mrkl_agent.tools))

        slack_chat.reply_to_message(
            self.slack_client,
            message_event,
            f"In COT mode!\n:toolbox: Available tools [{tool_names}]\n\n Thought:\n {text_buffer.summary()}",
        )
        slack_chat.reply_to_message(
            self.slack_client, message_event, f":check: {result}"
        )

    def register_handlers(self, handlers: list[MessageEventHandler]) -> None:
        self.hanlders.extend(handlers)
