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
        intents.message_content = (
            True  # Enable the message content intent for receiving message content
        )
        super().__init__(intents=intents)

    def add_proxy(self, proxy: BotProxy) -> None:
        self.proxies.append(proxy)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def on_message(self, message: Message):
        logger.info("recieve message", message=message)

        for proxy in self.proxies:
            proxy.on_message(message)

        # Ignore messages sent by the bot itself
        if message.author == self.user:
            return

        # Respond to a specific command
        if message.content.startswith("!hello"):
            await message.channel.send("Hello!")
