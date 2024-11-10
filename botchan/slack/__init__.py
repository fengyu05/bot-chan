import os

from slack_sdk import WebClient

from botchan.data_model.slack import (
    MessageEvent,
)
from botchan.logger import get_logger
from botchan.settings import BOT_CLIENT, SLACK_APP_OAUTH_TOKENS_FOR_WS
from botchan.slack.bot_client import SlackBotClient
from botchan.slack.slack_bot_proxy import SlackBotProxy

logger = get_logger(__name__)


def create_slack_client() -> WebClient | None:
    """
    This function returns a new instance of the Slack WebClient using the app-level tokens.
    Make sure to set your SLACK_APP_OAUTH_TOKENS_FOR_WS environment variable before calling this function.
    """
    if BOT_CLIENT != "SLACK":
        return None
    slack_token = os.environ["SLACK_APP_OAUTH_TOKENS_FOR_WS"]
    client = WebClient(token=slack_token)
    return client


if BOT_CLIENT == "SLACK":
    SLACK_CLIENT = create_slack_client()
    SLACK_BOT_CLIENT = SlackBotClient.get_instance(
        token=SLACK_APP_OAUTH_TOKENS_FOR_WS,
    )
    SLACK_BOT_PROXY = SlackBotProxy.get_instance(slack_client=SLACK_CLIENT)
    SLACK_BOT_CLIENT.add_proxy(SLACK_BOT_PROXY)

    @SLACK_BOT_CLIENT.event("message")
    def handle_message_events(event: dict) -> None:
        """Handle message to the bot."""
        logger.info("Message event", message_event=event)
        logger.info("typing", t=event["type"])
        message_event = MessageEvent(**event)
        if message_event.subtype == "message_created":
            SLACK_BOT_PROXY.on_message(message=message_event)
        elif message_event.subtype == "file_share":
            SLACK_BOT_PROXY.on_message(message=message_event)
        else:
            logger.info("message subtype has not handle", subtype=message_event.subtype)
