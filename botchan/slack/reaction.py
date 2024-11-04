"""Method for reaction.

All methods return a ReactionResponse.
"""

from abc import ABC

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from botchan.data_model.slack import MessageEvent, ReactionResponse
from botchan.logger import get_logger
from botchan.slack.exception import SlackResponseError

logger = get_logger(__name__)


class SlackReaction(ABC):
    slack_client: WebClient

    def add_reaction(self, event: MessageEvent, reaction_name: str) -> ReactionResponse:
        """
        Adds a reaction to a message.
        """
        try:
            response = self.slack_client.reactions_add(
                name=reaction_name, channel=event.channel, timestamp=event.ts
            )
            if response.status_code == 200 and response["ok"]:
                return ReactionResponse.from_api_response(response)
            else:
                raise SlackResponseError(response)
        except SlackApiError as e:
            logger.error("Error adding reaction", error=str(e))
