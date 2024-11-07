from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.core.bot_proxy import BotProxy
from botchan.data_model.slack import MessageEvent
from botchan.intent.intent_matcher_base import IntentMatcher
from botchan.intent.rag_intent_matcher import RagIntentMatcher
from botchan.logger import get_logger
from botchan.slack.chat import SlackChat
from botchan.slack.messages_fetcher import MessagesFetcher
from botchan.slack.reaction import SlackReaction
from botchan.utt.singleton import Singleton

logger = get_logger(__name__)


class SlackBotProxy(BotProxy, MessagesFetcher, SlackChat, SlackReaction, Singleton):
    slack_client: WebClient
    intent_matcher: IntentMatcher
    bot_user_id: str
    agents: list[MessageIntentAgent]

    def __init__(self, slack_client: WebClient):
        self.slack_client = slack_client
        self.bot_user_id = self.get_bot_user_id()
        self.chat_agent = OpenAiChatAgent(
            get_message_by_event=self.get_message_by_event
        )

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

    def on_message(self, message: MessageEvent) -> None:
        if not self._should_reply(message):
            return

        self.add_reaction(event=message, reaction_name="eyes")
        message_intent = self.intent_matcher.match_message_intent(message_event=message)
        if message_intent.unknown:
            self.chat_agent(message_event=message, message_intent=message_intent)
        else:
            for agent in self.agents:
                msgs = agent(message_event=message, message_intent=message_intent)
                if msgs is None:  ## agent didn't process this intent
                    continue
                for msg in msgs:
                    self.reply_to_message(event=message, text=msg)

    def get_bot_user_id(self) -> str:
        """
        This function returns the user ID of the bot currently connected to the Slack API.
        """
        try:
            # Call the auth.test method using the WebClient
            response = self.slack_client.auth_test()

            # Extract and return the bot user ID from the response
            return response["user_id"]

        except SlackApiError as e:
            logger.error("Error getting bot user ID", error=str(e))
