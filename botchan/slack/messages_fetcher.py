""" Messages Fetcher.
"""

import datetime
from typing import Callable, Optional, Union

import structlog
import toolz as T
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .data_model import Message, MessageEvent

logger = structlog.getLogger(__name__)


class MessagesFetcher:
    def __init__(self, client: WebClient) -> None:
        self.client = client

    @T.curry
    def _apply_filter(self, filter_func, messages):
        return T.filter(filter_func, messages)

    def _parse_ts_union(self, ts: Union[int, datetime.datetime, None]) -> int:
        return int(ts.timestamp()) if isinstance(ts, datetime.datetime) else ts

    def fetch(
        self,
        channel_id: str,
        thread_ts: Optional[str] = None,
        user_id: Optional[str] = None,
        oldest_ts: Union[int, datetime.datetime, None] = None,
        latest_ts: Union[int, datetime.datetime, None] = None,
        mentioned_user_id: Optional[str] = None,
        filters: Optional[list[Callable[[Message], bool]]] = None,
        limit: int = 1000,
    ) -> list[Message]:
        """
        Fetches messages from a specific Slack channel.

        Args:
            channel_id (str): The ID of the Slack channel to fetch messages from.
            thread_ts (str, optional): If provided, only fetch messages from this thread. Defaults to None.
            user_id (str, optional): If provided, only fetch messages sent by this user. Defaults to None.
            oldest_ts (Union[int, datetime.datetime, None], optional): If provided, only fetch messages newer than this timestamp. Can be either a Unix timestamp (int), or a datetime object. Defaults to None.
            latest_ts (Union[int, datetime.datetime, None], optional): If provided, only fetch messages older than this timestamp. Can be either a Unix timestamp (int), or a datetime object. Defaults to None.
            mentioned_user_id (str, optional): If provided, only fetch messages that mention this user. Defaults to None.
            filters (list[Callable[[Message], bool]], optional): A list of callable filters that each message must pass in order to be included in the results. Each filter should take a single argument (a message object) and return a boolean indicating whether the message should be included or not. Defaults to None.
            limit (int, optional): The maximum number of messages to fetch per API call. Defaults to 1000.

        Returns:
            list[Message]: A list of message objects representing the matching messages.
        """
        try:
            # Use 'conversations_reply' if thread_ts is specified otherwise 'conversations_history'
            _api = (
                self.client.conversations_replies
                if thread_ts
                else self.client.conversations_history
            )

            kwargs = {
                "channel": channel_id,
                "oldest": self._parse_ts_union(oldest_ts),
                "latest": self._parse_ts_union(latest_ts),
                "limit": limit,
                "ts": thread_ts,
            }
            response = _api(**kwargs)

            filters_function = filters if filters else []
            # Bind filter parameters with T.partial when necessary.
            if mentioned_user_id:
                filters_function += [
                    T.partial(Message.is_user_mentioned, user_id=mentioned_user_id)
                ]
            if user_id:
                filters_function += [T.partial(Message.is_from_userid, user_id=user_id)]

            messages = T.pipe(
                response["messages"],
                # 'apply Message.from_dict to each element' as a lamabda func
                lambda x: map(Message.parse_obj, x),
                # batch conver filters_function to a list of lambda that T.pipe expect
                *map(self._apply_filter, filters_function),
                list
            )
            return messages

        except SlackApiError as e:
            logger.error("Error fetching message", error=str(e))

    def get_most_replied_message(
        self,
        channel_id: str,
        oldest_ts: Union[int, datetime.datetime, None] = None,
        latest_ts: Union[int, datetime.datetime, None] = None,
        top_n: int = 1,
    ) -> list[Message]:
        """
        This function retrieves all messages with the most replies.
        """
        try:
            messages = self.fetch(
                channel_id=channel_id,
                oldest_ts=oldest_ts,
                latest_ts=latest_ts,
            )
            messages_with_reply_count = []
            for message in messages:
                messages_with_reply_count.append((message, message.reply_count))

            topn_messages = sorted(
                messages_with_reply_count, key=lambda x: x[1], reverse=True
            )[:top_n]

            # get the messages from the tuples
            return [msg_tuple[0] for msg_tuple in topn_messages]
        except SlackApiError as e:
            logger.error("Error get_most_replied_message", error=str(e))

    def get_last_message(self, channel_id: str) -> Message:
        return self.fetch(channel_id=channel_id, limit=1)[0]

    def fetch_message(self, message_event: MessageEvent) -> Optional[Message]:
        """
        Fetches a single message uniquely identified by its channel and timestamp.

        Args:
            message_event (dict): A dictionary containing 'channel' and 'ts' keys to identify the message.

        Returns:
            Optional[Message]: The fetched message object or None if not found.
        """
        try:
            response = self.client.conversations_history(
                channel=message_event.channel,
                inclusive=True,
                oldest=message_event.ts,
                latest=message_event.ts,
                limit=1,
            )

            if response["messages"]:
                messages = response["messages"]
                logger.debug("fetch_message get messages", messages=messages)
                return Message.parse_obj(messages[0])
            return None

        except SlackApiError as e:
            logger.error("Error fetching message", error=str(e))
            return None
