from typing import List, Optional

from pydantic import BaseModel

from .block import RichTextBlock
from .message import Message


class MessageEvent(BaseModel):
    type: str
    subtype: str = "message_created"
    channel: str
    channel_type: Optional[str] = None
    user: Optional[str] = None
    parent_user_id: Optional[str] = None  # only in reply message
    ts: str
    text: Optional[str]
    event_ts: str
    thread_ts: Optional[str] = None  # only in reply message

    @property
    def is_thread_root(self):
        return self.thread_ts is None

    @property
    def message_id(self):
        return f"{self.channel}|{self.ts}"

    @property
    def thread_message_id(self):
        return f"{self.channel}|{self.thread_ts or self.ts}"

    def is_user_mentioned(self, user_id: str) -> bool:
        return f"<@{user_id}>" in self.text


class MessageCreateEvent(MessageEvent):
    client_msg_id: str
    blocks: List[RichTextBlock] = []
    team: str


class MessageChangeEvent(MessageEvent):
    message: Optional[Message]
    previous_message: Optional[Message]
    hidden: bool

    @property
    def user(self):
        return self.message.user

    @property
    def text(self):
        return self.message.text


class MessageDeleteEvent(MessageChangeEvent):
    pass


class AppMentionEvent(MessageEvent):
    pass
