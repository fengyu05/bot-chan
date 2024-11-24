from pydantic import BaseModel

from .block import RichTextBlock
from .file_object import FileObject
from .message import Message


class MessageEvent(BaseModel):
    type: str
    subtype: str = "message_created"
    channel: str
    channel_type: str | None = None
    team: str | None = None
    user: str | None = None
    parent_user_id: str | None = None  # only in reply message
    ts: str
    text: str
    event_ts: str
    thread_ts: str | None = None  # only in reply message
    files: list[FileObject] | None = None
    upload: bool | None = None
    display_as_bot: bool | None = None
    client_msg_id: str | None = None
    blocks: list[RichTextBlock] | None = None

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

    @property
    def has_files(self) -> bool:
        return self.files is not None and len(self.files) > 0


class MessageChangeEvent(MessageEvent):
    message: Message | None
    previous_message: Message | None
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
