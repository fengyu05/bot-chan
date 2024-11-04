import logging
import signal
import sys

from botchan.discord.discord_bot_proxy import DiscordBotProxy
from botchan.logger import get_logger
from botchan.settings import BOT_CLIENT, LOG_LEVEL
from botchan.slack.slack_bot_proxy import SlackBotProxy
from botchan.types import AppType

logger = get_logger(__name__)


def start_server() -> None:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    # Registery cleanup on SIGNT
    signal.signal(signal.SIGINT, cleanup)

    if BOT_CLIENT == AppType.SLACK.name:
        proxy = SlackBotProxy.get_instance()
        proxy.start()
    elif BOT_CLIENT == AppType.DISCORD.name:
        proxy = DiscordBotProxy.get_instance()
        proxy.start()
    else:
        raise Exception(f"Unknown app type {BOT_CLIENT}")


def cleanup(sig, frame) -> None:  # pylint: disable=unused-argument
    logger.info("closing the server")
    # Do something
    logger.info("server closed with cleanup")
    sys.exit(0)
