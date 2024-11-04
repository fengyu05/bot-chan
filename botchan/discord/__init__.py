from botchan.discord.client import BotClient
from botchan.discord.discord_bot_proxy import DiscordBotProxy
from botchan.settings import BOT_CLIENT

if BOT_CLIENT == "DISCORD":
    BOT_CLIENT = BotClient.get_instance()
    BOT_PREOXY = DiscordBotProxy.get_instance(bot_client=BOT_CLIENT)
