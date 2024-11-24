import logging
import signal
import sys

from fluctlight.discord.bot_client import DiscordBotClient
from fluctlight.logger import get_logger
from fluctlight.settings import (
    BOT_CLIENT,
    DISCORD_BOT_TOKEN,
    LOG_LEVEL,
    SLACK_APP_LEVEL_TOKEN,
)
from fluctlight.slack.bot_client import SlackBotClient
from fluctlight.types import AppType

logger = get_logger(__name__)


def start_server() -> None:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    # Registery cleanup on SIGNT
    signal.signal(signal.SIGINT, cleanup)

    if BOT_CLIENT == AppType.SLACK.name:
        client = SlackBotClient.get_instance()
        client.run(SLACK_APP_LEVEL_TOKEN)
    elif BOT_CLIENT == AppType.DISCORD.name:
        client = DiscordBotClient.get_instance()
        client.run(DISCORD_BOT_TOKEN)
    else:
        raise Exception(f"Unknown app type {BOT_CLIENT}")


def cleanup(sig, frame) -> None:  # pylint: disable=unused-argument
    logger.info("closing the server")
    # Do something
    logger.info("server closed with cleanup")
    sys.exit(0)
