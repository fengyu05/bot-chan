import discord
from discord.message import Message
from discord.user import User

from fluctlight.agents.message_intent_agent import MessageIntentAgent
from fluctlight.agents.openai_chat_agent import OpenAiChatAgent
from fluctlight.core.bot_proxy import BotProxy
from fluctlight.data_model.interface import IChannel
from fluctlight.discord.adapter import Adapter
from fluctlight.discord.bot_client import DiscordBotClient
from fluctlight.discord.chat import DiscordChat
from fluctlight.discord.guild import DiscordGuild
from fluctlight.discord.reaction import DiscordReaction
from fluctlight.intent.intent_matcher_base import IntentMatcher
from fluctlight.intent.rag_intent_matcher import RagIntentMatcher
from fluctlight.logger import get_logger
from fluctlight.settings import DISCORD_BOT_DEVELOPER_ROLE
from fluctlight.utt.singleton import Singleton
from fluctlight.agents.character import create_default_character_agent

logger = get_logger(__name__)

DEFAULT_EYES_EMOJI = "eyes"


class DiscordBotProxy(BotProxy, DiscordChat, DiscordReaction, DiscordGuild, Singleton):
    client: DiscordBotClient
    agents: list[MessageIntentAgent]
    intent_matcher: IntentMatcher

    def __init__(self):
        super().__init__()
        self.adapter = Adapter()
        self.chat_agent = OpenAiChatAgent()
        self.agents = [
            create_default_character_agent(),
            self.chat_agent,
        ]
        self.intent_matcher = RagIntentMatcher(self.agents)

    def set_bot_client(self, client: DiscordBotClient) -> None:
        self.client = client

    def _should_reply(self, message: Message) -> bool:
        if message.author == self.bot_user:
            return False
        if message.content.startswith("!react"):
            logger.info("Ingore !react message", message=message)
            return False

        # Reply to direct messages
        if self._is_trust_dm(message) or self._bot_has_reply(message):
            return True
        if isinstance(
            message.channel, discord.TextChannel
        ) and self.bot_user.mentioned_in(message):
            return True

        return False

    def _is_trust_dm(self, message: Message) -> bool:
        """Trust DM is when the DM author is with developer role of Fluctlight."""
        if not isinstance(message.channel, discord.DMChannel):
            return False

        member = self.get_message_author_member(message)
        if not member:
            return False
        # Check if any of the author's roles match the developer role
        for role in member.roles:
            if role.name == DISCORD_BOT_DEVELOPER_ROLE:
                return True
        return False

    def _bot_has_reply(self, message: Message) -> bool:
        """The bot has reply to the message"""
        return (
            isinstance(message.channel, discord.Thread)
            and message.channel.owner_id == self.bot_user.id
        )

    async def on_message(self, message: Message) -> None:
        logger.debug("on message", message=message)
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
