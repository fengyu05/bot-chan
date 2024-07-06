import structlog
from slack_bolt import App

from botchan.agent import Agent
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


# In-memory storage for config settings (replace with your persistent storage)
config_settings = {
    "setting_1": "Default value 1",
    "setting_2": "Default value 2",
}

def open_modal(client, trigger_id):
    # Define a view (modal)
    view = {
        "type": "modal",
        "callback_id": "config_view",
        "title": {"type": "plain_text", "text": "Config Panel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "config_block_1",
                "label": {"type": "plain_text", "text": "Setting 1"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "setting_1",
                    "initial_value": config_settings["setting_1"],
                },
            },
            {
                "type": "input",
                "block_id": "config_block_2",
                "label": {"type": "plain_text", "text": "Setting 2"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "setting_2",
                    "initial_value": config_settings["setting_2"],
                },
            },
        ],
        "submit": {"type": "plain_text", "text": "Save"},
    }

    # Open the modal
    client.views_open(trigger_id=trigger_id, view=view)

@app.event("app_home_opened")
def update_home_tab(client, event):
    user_id = event["user"]

    # Define the Home tab view
    home_view = {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Current Configurations:*",
                },
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Setting 1:*\n{config_settings['setting_1']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Setting 2:*\n{config_settings['setting_2']}",
                    },
                ]
            }
        ]
    }

    # Publish the view to the Home tab
    client.views_publish(user_id=user_id, view=home_view)

# This handles the form submission from the modal
@app.view("config_view")
def handle_view_submission(ack, body, view, logger):
    ack()
    global config_settings  # Use global to update the in-memory config storage
    config_settings = {
        "setting_1": view["state"]["values"]["config_block_1"]["setting_1"]["value"],
        "setting_2": view["state"]["values"]["config_block_2"]["setting_2"]["value"],
    }
    user = body["user"]["id"]
    logger.info(f"Config submitted by user {user}: {config_settings}")
    
    # Update the home tab after saving the new settings
    update_home_tab(app.client, {"user": user}, logger)

