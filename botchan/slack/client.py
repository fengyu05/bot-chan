import os
from slack_sdk import WebClient


def create_slack_client():
    """
    This function returns a new instance of the Slack WebClient using the app-level tokens.
    Make sure to set your SLACK_APP_OAUTH_TOKENS_FOR_WS environment variable before calling this function.
    """
    slack_token = os.environ["SLACK_APP_OAUTH_TOKENS_FOR_WS"]
    client = WebClient(token=slack_token)
    return client
