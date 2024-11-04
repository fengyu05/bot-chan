import os

from slack_bolt import App
from slack_sdk import WebClient

from botchan.data_model import (
    MessageChangeEvent,
    MessageCreateEvent,
    MessageDeleteEvent,
    MessageEvent,
    MessageFileShareEvent,
)
from botchan.logger import get_logger
from botchan.settings import BOT_CLIENT, SLACK_APP_OAUTH_TOKENS_FOR_WS
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
    APP = App(
        token=SLACK_APP_OAUTH_TOKENS_FOR_WS,
    )
    BOT_PROXY = SlackBotProxy.get_instance(slack_app=APP, slack_client=SLACK_CLIENT)

    @APP.event("message")
    def handle_message_events(event: dict) -> None:
        """Handle message to the bot."""
        logger.debug("Message event", message_event=event)
        message_event = MessageEvent(**event)
        if message_event.subtype == "message_created":
            message_event = MessageCreateEvent(**event)
            BOT_PROXY.receive_message(message_event=message_event)
        elif message_event.subtype == "message_changed":
            message_event = MessageChangeEvent(**event)
        elif message_event.subtype == "message_deleted":
            message_event = MessageDeleteEvent(**event)
        elif message_event.subtype == "file_share":
            message_event = MessageFileShareEvent(**event)
            BOT_PROXY.receive_message(message_event=message_event)
        else:
            logger.info("message subtype has not handle", subtype=message_event.subtype)
