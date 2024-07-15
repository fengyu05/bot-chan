# In-memory storage for config settings (replace with your persistent storage)
CONFIG_SETTINGS = {
    "setting_1": "Default value 1",
    "setting_2": "Default value 2222",
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
                    "initial_value": CONFIG_SETTINGS["setting_1"],
                },
            },
            {
                "type": "input",
                "block_id": "config_block_2",
                "label": {"type": "plain_text", "text": "Setting 2"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "setting_2",
                    "initial_value": CONFIG_SETTINGS["setting_2"],
                },
            },
        ],
        "submit": {"type": "plain_text", "text": "Save"},
    }

    # Open the modal
    client.views_open(trigger_id=trigger_id, view=view)


def publish_home(client, event):
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
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Setting 1:*\n{CONFIG_SETTINGS['setting_1']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Setting 2:*\n{CONFIG_SETTINGS['setting_2']}",
                    },
                ],
            },
        ],
    }

    # Publish the view to the Home tab
    client.views_publish(user_id=user_id, view=home_view)
