import discord
from discord.message import Message

from botchan.core.bot_proxy import BotProxy
from botchan.logger import get_logger
from botchan.utt.singleton import Singleton

logger = get_logger(__name__)


class DiscordBotClient(discord.Client, Singleton):
    proxies: list[BotProxy] = []

    def __init__(self):
        # Define the intents you want your bot to have
        intents = discord.Intents.default()
        intents.members = True  # To access members list
        intents.message_content = True  # To access message content
        intents.guilds = True
        intents.messages = True
        super().__init__(command_prefix="!", intents=self.get_intents())

    def get_intents(self):
        """
        Configures and returns the bot's intents.

        Intents requested:
        - members: To access the member list of guilds.
        - message_content: To read the content of messages.
        - guilds: To receive events related to guilds.
        - messages: To process events involving messages.

        Returns:
            discord.Intents: The configured intents for the bot.
        """
        intents = discord.Intents.default()
        intents.members = True  # To access members list
        intents.message_content = True  # To access message content
        intents.guilds = True  # To receive guild-related events
        intents.messages = True  # To handle message events
        return intents

    def add_proxy(self, proxy: BotProxy) -> None:
        self.proxies.append(proxy)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def on_message(self, message: Message):
        for proxy in self.proxies:
            await proxy.on_message(message)
