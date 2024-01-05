# pylint: disable=unnecessary-lambda

import structlog
from slack_sdk import WebClient

from botchan.agents.chat_agent import MultiThreadChatAgent
from botchan.agents.mrkl import create_default_agent
from botchan.buffer_callback import BufferCallbackHandler
from botchan.message_event_handler import MessageEventHandler
from botchan.message_intent import (
    MessageIntent,
    get_message_intent,
    remove_emoji_prefix,
)
from botchan.settings import KNOWLEDGE_FOLDER
from botchan.slack import auth as slack_auth
from botchan.slack import chat as slack_chat
from botchan.slack import reaction as slack_reaction
from botchan.slack.data_model import MessageCreateEvent, MessageEvent
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
        self.chat_agent = MultiThreadChatAgent(
            bot_user_id=self.bot_user_id, fetcher=self.fetcher
        )
        self.tech_chat_agent = MultiThreadChatAgent(
            bot_user_id=self.bot_user_id,
            fetcher=self.fetcher,
            knowledge_folder=KNOWLEDGE_FOLDER,
        )

        self.hanlders = [
            # fmt: off
            MessageEventHandler(  ## Handle diaglog chat
                accept_intentions=[MessageIntent.CHAT],
                handler_func=lambda x: self._chat(x),  
            ),
            MessageEventHandler(  ## Handle diaglog chat
                accept_intentions=[MessageIntent.TECH_CHAT],
                handler_func=lambda x: self._tech_chat(x),  
            ),            
            MessageEventHandler(  ## Handle mrkl agent behaviors
                accept_intentions=[MessageIntent.MRKL_AGENT],
                handler_func=lambda x: self._chain_of_thought(x),
            )
            # fmt: on
        ]

    def register_handlers(self, handlers: list[MessageEventHandler]) -> None:
        self.hanlders.extend(handlers)

    def _should_reply(self, message_event: MessageCreateEvent) -> bool:
        return message_event.channel_type == "im" or message_event.is_user_mentioned(
            self.bot_user_id
        )

    def receive_message(self, message_event: MessageCreateEvent) -> None:
        # IM or mentioned
        if self._should_reply(message_event):
            slack_reaction.add_reaction(
                client=self.slack_client, event=message_event, reaction_name="eyes"
            )
            for handler in self.hanlders:
                handler.handle(message_event)

    ## agent handle functions
    def _chat(self, message_event: MessageEvent) -> None:
        output = self.chat_agent.run(
            message_event, message_intent=get_message_intent(message=message_event)
        )
        slack_chat.reply_to_message(self.slack_client, message_event, output)

    def _tech_chat(self, message_event: MessageEvent) -> None:
        output = self.tech_chat_agent.run(
            message_event, message_intent=get_message_intent(message=message_event)
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
            f"Botchan is in COT mode, available tools :toolbox: [{tool_names}] :toolbox:\n\n :thought_balloon:\n {text_buffer.summary()}",
        )
        slack_chat.reply_to_message(
            self.slack_client, message_event, f":check: {result}"
        )
