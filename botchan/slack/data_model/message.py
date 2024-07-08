from typing import List, Optional

from pydantic import BaseModel

from .block import RichTextBlock
from .bot_profile import BotProfile


class Message(BaseModel):
    client_msg_id: Optional[str]
    type: str
    text: str
    user: str
    ts: str
    blocks: List[RichTextBlock]
    team: str
    edited: Optional[dict]
    thread_ts: Optional[str]
    reply_count: int = 0
    reply_users_count: int = 0
    latest_reply: Optional[str] = None
    reply_users: List[str] = []
    is_locked: Optional[bool] = None
    subscribed: Optional[bool] = None
    hidden: Optional[bool] = None
    last_read: Optional[str]
    bot_id: Optional[str] = None
    app_id: Optional[str] = None
    bot_profile: Optional[BotProfile] = None

    def is_user_mentioned(self, user_id: str) -> bool:
        return f"<@{user_id}>" in self.text

    def is_from_userid(self, user_id: str) -> bool:
        return self.user == user_id

    def has_reply_from_user(self, user_id: str) -> bool:
        return user_id in self.reply_users

    def message_link(self, channel: str) -> str:
        return f"https://{self.team}.slack.com/archives/{channel}/p{self.ts}"

    @property
    def has_files(self) -> bool:
        return hasattr(self, 'files') and self.files
            