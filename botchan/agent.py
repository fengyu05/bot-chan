# pylint: disable=unnecessary-lambda
# pylint: disable=unused-argument
from typing import Union

import structlog
from slack_sdk import WebClient

from botchan.agents.knowledge_agent import KnowledgeChatAgent, ResultType
from botchan.agents.mrkl_agent import create_default_agent
from botchan.buffer_callback import BufferCallbackHandler
from botchan.message_event_handler import MessageEventHandler
from botchan.message_intent import MessageIntent, remove_emoji_prefix
from botchan.slack import auth as slack_auth
from botchan.slack import chat as slack_chat
from botchan.slack import reaction as slack_reaction
from botchan.slack.data_model import (
    MessageCreateEvent,
    MessageEvent,
    MessageFileShareEvent,
)
from botchan.slack.messages_fetcher import MessagesFetcher

logger = structlog.getLogger(__name__)


class Agent:
    slack_client: WebClient
    fetcher: MessagesFetcher
    bot_user_id: str
    hanlders: list[MessageEventHandler]

    def __init__(self, slack_client: WebClient):
        self.slack_client = slack_client
        self.fetcher = MessagesFetcher(self.slack_client)
        self.bot_user_id = slack_auth.get_bot_user_id(self.slack_client)

        # Config all agents
        self.mrkl_agent = create_default_agent()
        self.knowledge_chat_agent = KnowledgeChatAgent()

        self.hanlders = [
            # fmt: off
            MessageEventHandler(  ## Handle diaglog chat
                accept_intentions=[MessageIntent.CHAT],
                handler_func=lambda event, intent: self._chat(event, intent),
            ),
            MessageEventHandler(  ## Handle knowledge learning
                accept_intentions=[MessageIntent.KNOW],
                handler_func=lambda event, intent: self._learn_knowledge(event, intent),  
                cant_handle_func=lambda event, intent: self._show_howto_learn(event, intent),
            ),            
            MessageEventHandler(  ## Handle mrkl agent behaviors
                accept_intentions=[MessageIntent.MRKL_AGENT],
                handler_func=lambda event, intent: self._chain_of_thought(event, intent),
            )
            # fmt: on
        ]

    def register_handlers(self, handlers: list[MessageEventHandler]) -> None:
        self.hanlders.extend(handlers)

    def _should_reply(self, message_event: MessageCreateEvent) -> bool:
        return message_event.channel_type == "im" or message_event.is_user_mentioned(
            self.bot_user_id
        )

    def receive_message(
        self, message_event: Union[MessageCreateEvent, MessageFileShareEvent]
    ) -> None:
        if self._should_reply(message_event):  # IM or mentioned
            slack_reaction.add_reaction(
                client=self.slack_client, event=message_event, reaction_name="eyes"
            )
            for handler in self.hanlders:
                handler.handle(message_event=message_event)

    def _chain_of_thought(
        self, message_event: MessageEvent, intent: MessageIntent
    ) -> None:
        text_buffer = BufferCallbackHandler()
        result = self.mrkl_agent.run(
            remove_emoji_prefix(message_event.text), callbacks=[text_buffer]
        )
        tool_names = ",".join(map(lambda x: x.name, self.mrkl_agent.tools))

        slack_chat.reply_to_message(
            self.slack_client,
            message_event,
            f"Botchan is in COT mode, available tools :toolbox: [{tool_names}] :toolbox:\n\n :thought_balloon:\n {text_buffer.summary()}",
        )
        slack_chat.reply_to_message(
            self.slack_client, message_event, f":check: {result}"
        )

    def _learn_knowledge(
        self, message_event: MessageEvent, intent: MessageIntent
    ) -> None:
        self.knowledge_chat_agent.learn_knowledge(message_event)
        slack_chat.reply_to_message(
            self.slack_client,
            message_event,
            "Thank you for providing the information. I've learn it and keep them in my knowledge database.",
        )

    def _show_howto_learn(
        self, message_event: MessageEvent, intent: MessageIntent
    ) -> None:
        if intent == MessageIntent.UNKNOWN:
            slack_chat.reply_to_message(
                self.slack_client,
                message_event,
                "Start message with emoji :rem:(rem), :know:(know), :learn:(learn) to teach me new knowledge.",
            )

    def _chat(self, message_event: MessageEvent, intent: MessageIntent) -> None:
        result_type, output = self.knowledge_chat_agent.qa(message_event)
        if result_type == ResultType.RETRIEVAL:
            slack_chat.reply_to_message(
                self.slack_client,
                message_event,
                "We found a doc in our knowledge base to related to your question.",
            )
        slack_chat.reply_to_message(self.slack_client, message_event, output)
