import structlog
from functools import cache
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = structlog.getLogger(__name__)


@cache
def get_bot_user_id(client: WebClient) -> str:
    """
    This function returns the user ID of the bot currently connected to the Slack API.
    """
    try:
        # Call the auth.test method using the WebClient
        response = client.auth_test()

        # Extract and return the bot user ID from the response
        return response["user_id"]

    except SlackApiError as e:
        logger.error("Error getting bot user ID", error=str(e))
