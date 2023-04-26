from collections import defaultdict
from enum import Enum
from typing import Union

from botchan.slack.data_model import Message, MessageEvent


class MessageIntent(Enum):
    UNKNOWN = 0
    CHAT = 1
    REPORT = 2
    # Add more intent here


_EMOJI_INTENT_MAP = {
    MessageIntent.REPORT: ["report"],
}

_INTENT_BY_EMOJI = {
    emoji: intent for intent, emojis in _EMOJI_INTENT_MAP.items() for emoji in emojis
}


def get_message_intent(message: Union[Message, MessageEvent]):
    text = message.text
    for emoji in _INTENT_BY_EMOJI:
        if text.startswith(f":{emoji}:"):
            return _INTENT_BY_EMOJI[emoji]
    return MessageIntent.CHAT
