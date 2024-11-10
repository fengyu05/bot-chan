from pydantic import BaseModel

from .block import RichTextBlock
from .bot_profile import BotProfile
from .file_object import FileObject


class Message(BaseModel):
    client_msg_id: str | None = None
    type: str
    text: str
    user: str
    ts: str
    blocks: list[RichTextBlock] | None = None
    team: str | None = None
    edited: dict | None = None
    thread_ts: str | None = None
    reply_count: int = 0
    reply_users_count: int = 0
    latest_reply: str | None = None
    reply_users: list[str] = []
    is_locked: bool | None = None
    subscribed: bool | None = None
    hidden: bool | None = None
    last_read: str | None = None
    bot_id: str | None = None
    app_id: str | None = None
    bot_profile: BotProfile | None = None
    files: list[FileObject] | None = None

    def is_user_mentioned(self, user_id: str) -> bool:
        return f"<@{user_id}>" in self.text

    def is_from_userid(self, user_id: str) -> bool:
        return self.user == user_id

    def has_reply_from_user(self, user_id: str) -> bool:
        return user_id in self.reply_users

    def message_link(self, channel: str) -> str:
        return f"https://{self.team}.slack.com/archives/{channel}/p{self.ts}"
