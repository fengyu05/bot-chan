from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class MessageIntentType(Enum):
    UNKNOWN = 0
    CHAT = 1
    KNOW = 2
    MIAO = 3
    EXPERT = 4

    @staticmethod
    def from_str(label):
        for intent in MessageIntentType:
            if label == intent.name.upper():
                return intent
        raise NotImplementedError("The provided label does not match any MessageIntent")


class MessageIntent(BaseModel):
    type: MessageIntentType
    key: Optional[str] = None

    def __eq__(self, other: object) -> bool:
        """Override the equality operator to compare `type` and `key` fields only."""
        if isinstance(other, MessageIntent):
            return self.type == other.type and self.key == other.key
        return False

    def __repr__(self):
        field_strings = [f"{key}: {value}" for key, value in self.dict().items()]
        return "\n".join(field_strings)


def create_intent(type_name: str, key: Optional[str] = None) -> MessageIntent:
    return MessageIntent(type=MessageIntentType.from_str(type_name), key=key)


_EMOJI_INTENT_MAP = {
    MessageIntentType.KNOW: ["know", "learn"],
    MessageIntentType.MIAO: ["cat"],
    MessageIntentType.EXPERT: ["expert"],
}

_INTENT_BY_EMOJI = {
    emoji: intent for intent, emojis in _EMOJI_INTENT_MAP.items() for emoji in emojis
}


def get_message_intent_by_emoji(text: str) -> MessageIntent:
    for emoji in _INTENT_BY_EMOJI:
        if text.startswith(f":{emoji}:"):
            return _INTENT_BY_EMOJI[emoji]
    return MessageIntent(type=MessageIntentType.UNKNOWN)
