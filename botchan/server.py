import logging
import signal
import sys

from slack_bolt.adapter.socket_mode import SocketModeHandler

from botchan.app import app
from botchan.settings import LOG_LEVEL, SLACK_APP_LEVEL_TOKEN

from botchan.logger import get_logger

logger = get_logger(__name__)


def start_server(port: int = 3000) -> None:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))

    # Registery cleanup on SIGNT
    signal.signal(signal.SIGINT, cleanup)

    logger.info("starting server at", port=port)
    handler = SocketModeHandler(app_token=SLACK_APP_LEVEL_TOKEN, app=app)
    handler.start()


def cleanup(sig, frame) -> None:  # pylint: disable=unused-argument
    logger.info("closing the server")
    # Do something
    logger.info("server closed with cleanup")
    sys.exit(0)
