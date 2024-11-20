from fluctlight.discord.bot_client import DiscordBotClient
from fluctlight.discord.discord_bot_proxy import DiscordBotProxy
from fluctlight.settings import BOT_CLIENT

if BOT_CLIENT == "DISCORD":
    DISCORD_BOT_CLIENT = DiscordBotClient.get_instance()
    DISCORD_PROXY = DiscordBotProxy.get_instance()

    DISCORD_BOT_CLIENT.add_proxy(DISCORD_PROXY)
    DISCORD_PROXY.set_bot_client(DISCORD_BOT_CLIENT)
