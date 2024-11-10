from enum import Enum

from pydantic import BaseModel

from botchan.data_model.interface.common import IdType


# Define the Pydantic model with a _type field
class IChannel(BaseModel):
    class Type(Enum):
        DM = "DM"
        TEXT_CHANNEL = "TEXT_CHANNEL"
        THREAD = "THREAD"
        GROUP = "GROUP"
        NOT_SUPPORT = "NOT_SUPPORT"

    id: IdType
    channel_type: Type
