import discord
from discord.message import Message
from discord.user import User

from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.core.bot_proxy import BotProxy
from botchan.data_model.interface import IChannel
from botchan.discord.adapter import Adapter
from botchan.discord.bot_client import DiscordBotClient
from botchan.discord.chat import DiscordChat
from botchan.discord.reaction import DiscordReaction
from botchan.intent.intent_matcher_base import IntentMatcher
from botchan.intent.rag_intent_matcher import RagIntentMatcher
from botchan.logger import get_logger
from botchan.utt.singleton import Singleton

logger = get_logger(__name__)

DEFAULT_EYES_EMOJI = "eyes"


class DiscordBotProxy(BotProxy, DiscordChat, DiscordReaction, Singleton):
    client: DiscordBotClient
    agents: list[MessageIntentAgent]
    intent_matcher: IntentMatcher

    def __init__(self):
        super().__init__()
        self.adapter = Adapter()
        self.chat_agent = OpenAiChatAgent(get_message_by_event=None)
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

    def set_bot_client(self, client: DiscordBotClient) -> None:
        self.client = client

    def _should_reply(self, message: Message) -> bool:
        if message.author == self.bot_user:
            return False
        if message.content.startswith("!react"):
            logger.info("Ingore !react message")
            return False

        # Reply to direct messages
        if isinstance(message.channel, discord.DMChannel):
            return True
        # Reply to thread that create by the bot
        if isinstance(message.channel, discord.Thread):
            if message.channel.owner_id == self.bot_user.id:
                return True
        # Reply if the bot is mentioned in a guild channel
        if isinstance(
            message.channel, discord.TextChannel
        ) and self.bot_user.mentioned_in(message):
            return True

    async def on_message(self, message: Message) -> None:
        if not self._should_reply(message):
            return

        imessage = self.adapter.cast_message(message)
        logger.info("imessage", message=imessage)

        if imessage.channel.channel_type == IChannel.Type.TEXT_CHANNEL:
            thread = await message.create_thread(
                name=imessage.re_topic, auto_archive_duration=60
            )
        elif imessage.channel.channel_type == IChannel.Type.THREAD:
            # append to existing thread
            thread = message.thread
        else:
            thread = None

        await self.add_reaction(message=message, reaction_name=DEFAULT_EYES_EMOJI)
        message_intent = self.intent_matcher.match_message_intent(message=imessage)
        if message_intent.unknown:
            self.chat_agent(message=imessage, message_intent=message_intent)
        else:
            for agent in self.agents:
                response_texts = agent(message=imessage, message_intent=message_intent)
                if response_texts is None:  ## agent didn't process this intent
                    continue
                for text in response_texts:
                    await self.reply_to_message(
                        message=message, thread=thread, text=text
                    )

    @property
    def bot_user(self) -> User:
        return self.client.user
