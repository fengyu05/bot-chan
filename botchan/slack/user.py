from abc import ABC

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from botchan.data_model.slack import UserProfile
from botchan.logger import get_logger
from botchan.slack.exception import SlackResponseError

logger = get_logger(__name__)


class SlackReaction(ABC):
    slack_client: WebClient

    def get_user_profile(self, user_id: str) -> UserProfile:
        try:
            response = self.slack_client.users_profile_get(user=user_id)
            if not response["ok"]:
                raise SlackResponseError(response=response)

            return UserProfile.from_dict(response["profile"])
        except SlackApiError as e:
            logger.error("Error getting user profile", error=str(e))
