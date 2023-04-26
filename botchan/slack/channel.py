from typing import Any, Optional

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack import user as slack_user
from .slack.data_model import UserProfile, ChannelType

logger = structlog.getLogger(__name__)


def get_channels(
    client: WebClient, channel_type: ChannelType = ChannelType.PUBLIC_CHANNEL
) -> list[str]:
    """
    This function retrieves a list of all public channels that the bot is a member of.
    """
    try:
        # Call the conversations.list method using the WebClient and the appropriate arguments
        response = client.conversations_list(types=channel_type.value)

        # Extract the channel IDs from the response and return them as a list
        channels = response["channels"]
        channel_ids = [channel["id"] for channel in channels]
        return channel_ids

    except SlackApiError as e:
        logger.info("Error retrieving public channels", error=str(e))


def get_channel_members(client: WebClient, channel_id: str) -> list[str]:
    try:
        response = client.conversations_members(channel=channel_id)
        members = response["members"]
        return members
    except SlackApiError as e:
        logger("Error getting conversation members", error=str(e))


def get_channel_members_profile(
    client: WebClient, channel_id: str
) -> list[UserProfile]:
    user_ids = get_channel_members(client=client, channel_id=channel_id)
    return [slack_user.get_user_profile(client, user_id) for user_id in user_ids]
