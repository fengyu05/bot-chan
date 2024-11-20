from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse

from fluctlight.data_model.slack import MessageEvent
from fluctlight.logger import get_logger

logger = get_logger(__name__)


class SlackChat:
    slack_client: WebClient

    def _post_message(
        self, channel_id: str, text: str, thread_ts: Optional[str] = None
    ) -> SlackResponse:
        """
        Posts a message to a given Slack channel using the provided WebClient.

        Parameters:
            channel_id (str): The ID of the channel to which the message should be posted.
            text (str): The message content.
            thread_ts (Optional[str]): Optional thread timestamp to reply in a thread.
        """
        return self.slack_client.chat_postMessage(
            channel=channel_id, text=text, thread_ts=thread_ts
        )

    def send_message(self, channel_id: str, text: str) -> SlackResponse:
        """
        This function sends a Slack message to the specified channel using the given client object.
        """
        try:
            return self._post_message(channel_id=channel_id, text=text)
        except SlackApiError as e:
            logger.error("Error sending message", error=str(e))

    def reply_to_message(self, event: MessageEvent, text: str) -> SlackResponse:
        """
        This function sends a reply message to the channel where the original message was sent.
        """
        try:
            return self._post_message(
                channel_id=event.channel, text=text, thread_ts=event.ts
            )
        except SlackApiError as e:
            logger.error("Error sending message", error=str(e))
