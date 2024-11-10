from pydantic import BaseModel

from botchan.data_model.interface.attachment import IAttachment
from botchan.data_model.interface.channel import IChannel
from botchan.data_model.interface.common import IdType


class IMessage(BaseModel):
    text: str
    ts: float  # This is in second, compatible with Twttier snowflake
    message_id: IdType
    thread_message_id: IdType
    channel: IChannel
    attachments: list[IAttachment] | None = None

    @property
    def re_topic(self) -> str:
        """A brief topic about the text, re: `text`, limit to 20 chars"""
        # For simplicity, we'll just take up to the first 20 characters
        if len(self.text) > 20:
            return f"re: {self.text[:17]}..."
        return f"re: {self.text}"

    @property
    def has_attachments(self) -> bool:
        return self.attachments is not None and len(self.attachments) > 0

    @property
    def is_thread_root(self):
        return self.message_id == self.thread_message_id
