# pylint: disable=unnecessary-lambda
# pylint: disable=unused-argument
import structlog
from slack_sdk import WebClient

from botchan.agents import MessageIntentAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.intent.intent_macher_base import IntentMatcher
from botchan.intent.rag_intent_matcher import RagIntentMatcher
from botchan.settings import DEBUG_MODE
from botchan.slack import auth as slack_auth
from botchan.slack import chat as slack_chat
from botchan.slack import reaction as slack_reaction
from botchan.slack.data_model import MessageEvent
from botchan.slack.messages_fetcher import MessagesFetcher

logger = structlog.getLogger(__name__)


class MessageMultiIntentAgent:
    slack_client: WebClient
    fetcher: MessagesFetcher
    intent_matcher: IntentMatcher
    bot_user_id: str
    agents: list[MessageIntentAgent]

    def __init__(self, slack_client: WebClient):
        self.slack_client = slack_client
        self.fetcher = MessagesFetcher(self.slack_client)
        self.bot_user_id = slack_auth.get_bot_user_id(self.slack_client)
        self.chat_agent = OpenAiChatAgent()
        from botchan.agents.expert.poem_translate import (
            create_poems_translation_task_agent,
        )
        from botchan.agents.expert.shopping_assist import (
            create_shopping_assisist_task_agent,
        )

        self.agents = [
            create_poems_translation_task_agent(),
            create_shopping_assisist_task_agent(),
            self.chat_agent,
        ]
        self.intent_matcher = RagIntentMatcher(self.agents)

    def _should_reply(self, message_event: MessageEvent) -> bool:
        return message_event.channel_type == "im" or message_event.is_user_mentioned(
            self.bot_user_id
        )

    def receive_message(self, message_event: MessageEvent) -> None:
        if self._should_reply(message_event):  # IM or mentioned
            slack_reaction.add_reaction(
                client=self.slack_client, event=message_event, reaction_name="eyes"
            )
            message_intent = self.intent_matcher.match_message_intent(
                message_event=message_event
            )
            if DEBUG_MODE:
                slack_chat.reply_to_message(
                    self.slack_client, message_event, f"Matched itent {message_intent}"
                )
            if message_intent.unknown:
                self.chat_agent(
                    message_event=message_event, message_intent=message_intent
                )
            else:
                for agent in self.agents:
                    msgs = agent(
                        message_event=message_event, message_intent=message_intent
                    )
                    if msgs is None:  ## agent didn't process this intent
                        continue
                    for msg in msgs:
                        slack_chat.reply_to_message(
                            self.slack_client, message_event, msg
                        )
