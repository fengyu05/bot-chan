import re
from enum import Enum
from typing import Union

from botchan.slack.data_model import Message, MessageEvent


class MessageIntent(Enum):
    UNKNOWN = 0
    CHAT = 1
    REPORT = 2
    MRKL_AGENT = 3  ## using chain-of-thought agent, all tools
    # Add more intent here


_EMOJI_INTENT_MAP = {
    MessageIntent.REPORT: ["report"],
    MessageIntent.MRKL_AGENT: ["thought", "chains"],
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


def remove_emoji_prefix(text: str) -> str:
    """
    Remove the emojie prefix from text. The emoji prefix is wrap in ':' sign
    ":shell:ABC" => "ABC"
    ":thought: what is 2 + 2?" => "what is 2 + 2?"
    """
    result = re.sub(r":.*?:", "", text)
    return result.strip()  # strip off any leading/trailing white spaces
