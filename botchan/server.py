import logging
import signal
import sys

from botchan.logger import get_logger
from botchan.settings import LOG_LEVEL
from botchan.slack.slack_bot_proxy import SlackBotProxy
from botchan.types import AppType

logger = get_logger(__name__)


def start_server(app_type: AppType = AppType.SLACK) -> None:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    # Registery cleanup on SIGNT
    signal.signal(signal.SIGINT, cleanup)

    if app_type == AppType.SLACK:
        proxy = SlackBotProxy.get_instance()
        proxy.start()
    else:
        raise Exception(f"Unknown app type {app_type}")


def cleanup(sig, frame) -> None:  # pylint: disable=unused-argument
    logger.info("closing the server")
    # Do something
    logger.info("server closed with cleanup")
    sys.exit(0)
