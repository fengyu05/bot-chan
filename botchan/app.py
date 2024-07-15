import structlog
from slack_bolt import App

from botchan.agent import Agent
from botchan.app_home import CONFIG_SETTINGS, publish_home
from botchan.settings import SLACK_APP_OAUTH_TOKENS_FOR_WS
from botchan.slack.client import create_slack_client
from botchan.slack.data_model import (
    MessageChangeEvent,
    MessageCreateEvent,
    MessageDeleteEvent,
    MessageEvent,
    MessageFileShareEvent,
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
    logger.debug("Message event", message_event=event)
    message_event = MessageEvent(**event)
    if message_event.subtype == "message_created":
        message_event = MessageCreateEvent(**event)
        agent.receive_message(message_event=message_event)
    elif message_event.subtype == "message_changed":
        message_event = MessageChangeEvent(**event)
    elif message_event.subtype == "message_deleted":
        message_event = MessageDeleteEvent(**event)
    elif message_event.subtype == "file_share":
        message_event = MessageFileShareEvent(**event)
        agent.receive_message(message_event=message_event)
    else:
        logger.info("message subtype has not handle", subtype=message_event.subtype)


# @app.event("app_mention")
# def handle_mention_events(event: dict):
#     """Handles events related to mentions in public channels."""
#     logger.debug("app_mention event", _event=event)
#     mention_event = AppMentionEvent(**event)
#     logger.debug("app_mention event parsed", mention_event=mention_event)


# @app.event("app_home_opened")
# def update_home_tab(client, event):
#     publish_home(client=client, event=event)


# # This handles the form submission from the modal
# @app.view("config_view")
# def handle_view_submission(ack, body, view):
#     ack()
#     CONFIG_SETTINGS["setting_1"] = view["state"]["values"]["config_block_1"][
#         "setting_1"
#     ]["value"]
#     CONFIG_SETTINGS["setting_1"] = view["state"]["values"]["config_block_2"][
#         "setting_2"
#     ]["value"]

#     user = body["user"]["id"]
#     logger.info(f"Config submitted by user {user}: {CONFIG_SETTINGS}")

#     # Update the home tab after saving the new settings
#     update_home_tab(app.client, {"user": user})
