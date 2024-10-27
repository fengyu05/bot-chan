from pydantic import BaseModel, field_validator

_UNKNOWN = "unknown"
_METHOD = "method"
_EMOJI = "emoji"


class MessageIntent(BaseModel):
    key: str
    metadata: dict[str, str | bool | float | int | None] = {}

    @field_validator("key")
    @classmethod
    def uppercase_key(cls, v):
        if not isinstance(v, str):
            raise ValueError("The key must be a string.")
        return v.upper()

    @property
    def unknown(self) -> bool:
        return _UNKNOWN in self.metadata

    def method(self) -> str:
        return str(self.metadata.get(_METHOD, ""))

    def equal_wo_metadata(self, other: "MessageIntent") -> bool:
        return self.key == other.key


def create_intent(key: str | None = None, unknown: bool = False) -> MessageIntent:
    if unknown:
        return MessageIntent(key="", metadata={_UNKNOWN: True})
    assert key, "key must present"
    return MessageIntent(key=key)


class IntentCandidate(BaseModel):
    CustomerUnderstanding: str  # System's interpretation of the message
    IntentName1: str  # Primary intent matching the user's need
    IntentName2: str  # Secondary intent somewhat matching the need
    IntentClarification: str  # Explanation of chosen intents' relevance


_EMOJI_INTENT_MAP = {
    "miao": ["cat"],
}

_INTENT_BY_EMOJI = {
    emoji: intent for intent, emojis in _EMOJI_INTENT_MAP.items() for emoji in emojis
}


def get_message_intent_by_emoji(text: str) -> MessageIntent:
    for emoji in _INTENT_BY_EMOJI:
        if text.startswith(f":{emoji}:"):
            return MessageIntent(
                key=_INTENT_BY_EMOJI[emoji], metadata={_METHOD: _EMOJI, _EMOJI: emoji}
            )
    return MessageIntent(key="", metadata={_UNKNOWN: True, _METHOD: _EMOJI})
