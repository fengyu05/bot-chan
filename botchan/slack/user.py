from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .data_model import UserProfile
from .exception import SlackResponseError

from botchan.logger import get_logger

logger = get_logger(__name__)


def get_user_profile(client: WebClient, user_id) -> UserProfile:
    try:
        response = client.users_profile_get(user=user_id)
        if not response["ok"]:
            raise SlackResponseError(response=response)

        return UserProfile.from_dict(response["profile"])
    except SlackApiError as e:
        logger.error("Error getting user profile", error=str(e))
