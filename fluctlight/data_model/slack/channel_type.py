from enum import Enum


class ChannelType(Enum):
    PUBLIC_CHANNEL = "public_channel"
    PRIVATE_CHANNEL = "private_channel"
    MPIM = "mpim"
    IM = "im"
