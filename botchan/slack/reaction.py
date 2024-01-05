""" Method for reaction.

All methods return a ReactionResponse.
"""
import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .data_model import MessageEvent, ReactionResponse
from .exception import SlackResponseError

logger = structlog.getLogger(__name__)


def add_reaction(
    client: WebClient, event: MessageEvent, reaction_name: str
) -> ReactionResponse:
    """
    Adds a reaction to a message.
    """
    try:
        response = client.reactions_add(
            name=reaction_name, channel=event.channel, timestamp=event.ts
        )
        if response.status_code == 200 and response["ok"]:
            return ReactionResponse.from_api_response(response)
        else:
            raise SlackResponseError(response)
    except SlackApiError as e:
        logger.error("Error adding reaction", error=str(e))
