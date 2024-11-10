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
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        super().__init__(command_prefix="!", intents=intents)

    def add_proxy(self, proxy: BotProxy) -> None:
        self.proxies.append(proxy)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def on_message(self, message: Message):
        for proxy in self.proxies:
            await proxy.on_message(message)
