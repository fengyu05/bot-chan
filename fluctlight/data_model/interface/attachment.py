from pydantic import BaseModel

from fluctlight.data_model.interface.common import IdType


class IAttachment(BaseModel):
    id: IdType
    content_type: str
    filename: str
    url: str
    subtype: str | None = None
