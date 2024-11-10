"""Method for reaction.

All methods return a ReactionResponse.
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse

from botchan.data_model.slack import MessageEvent
from botchan.logger import get_logger

logger = get_logger(__name__)


class SlackReaction:
    slack_client: WebClient

    def add_reaction(self, event: MessageEvent, reaction_name: str) -> SlackResponse:
        """
        Adds a reaction to a message.
        """
        try:
            return self.slack_client.reactions_add(
                name=reaction_name, channel=event.channel, timestamp=event.ts
            )
        except SlackApiError as e:
            logger.error("Error adding reaction", error=str(e))
