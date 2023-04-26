from typing import Any

import structlog
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from botchan.agent import Agent
from botchan.settings import SLACK_APP_OAUTH_TOKENS_FOR_WS
from botchan.slack.client import create_slack_client
from botchan.slack.data_model import (
    AppMentionEvent,
    MessageChangeEvent,
    MessageCreateEvent,
    MessageDeleteEvent,
    MessageEvent,
)

logger = structlog.get_logger(__name__)
slack_client = create_slack_client()

agent = Agent(slack_client=slack_client)

app = App(
    token=SLACK_APP_OAUTH_TOKENS_FOR_WS,
)


@app.event("message")
def handle_message_events(event: dict) -> None:
    """Handle message to the bot."""
    logger.debug("message event", _event=event)
    message_event = MessageEvent(**event)
    if message_event.subtype == "message_created":
        message_event = MessageCreateEvent(**event)
        agent.receive_message(message_event=message_event)
    elif message_event.subtype == "message_changed":
        message_event = MessageChangeEvent(**event)
    elif message_event.subtype == "message_deleted":
        message_event = MessageDeleteEvent(**event)
    else:
        logger.info("message subtype has not handle", subtype=message_event.subtype)


# @app.event("app_mention")
# def handle_mention_events(event: dict):
#     """Handles events related to mentions in public channels."""
#     logger.debug("app_mention event", _event=event)
#     mention_event = AppMentionEvent(**event)
#     logger.debug("app_mention event parsed", mention_event=mention_event)
