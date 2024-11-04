from discord.message import Message

from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.core.bot_proxy import BotProxy
from botchan.data_model.slack import MessageEvent
from botchan.intent.intent_matcher_base import IntentMatcher
from botchan.intent.rag_intent_matcher import RagIntentMatcher
from botchan.logger import get_logger
from botchan.settings import DEBUG_MODE, DISCORD_BOT_TOKEN
from botchan.utt.singleton import Singleton

logger = get_logger(__name__)


class DiscordBotProxy(BotProxy, Singleton):
    def _should_reply(self, message_event: MessageEvent) -> bool:
        return message_event.channel_type == "im" or message_event.is_user_mentioned(
            self.bot_user_id
        )

    def on_message(self, message: MessageEvent | Message) -> None:
        logger.info("on message", message=message)
