from pydantic import BaseModel

from botchan.data_model.interface.common import IdType


class IAttachment(BaseModel):
    id: IdType
    content_type: str
    filename: str
    url: str
