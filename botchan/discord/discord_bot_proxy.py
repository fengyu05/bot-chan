from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.core.bot_proxy import BotProxy
from botchan.data_model import MessageEvent
from botchan.discord.client import BotClient
from botchan.intent.intent_matcher_base import IntentMatcher
from botchan.intent.rag_intent_matcher import RagIntentMatcher
from botchan.logger import get_logger
from botchan.settings import DEBUG_MODE, DISCORD_BOT_TOKEN
from botchan.utt.singleton import Singleton

logger = get_logger(__name__)


class DiscordBotProxy(BotProxy, Singleton):
    def __init__(self, bot_client: BotClient):
        self.bot_client = bot_client

    def start(self) -> None:
        self.bot_client.run(DISCORD_BOT_TOKEN)

    def receive_message(self, message_event: MessageEvent) -> None:
        pass
