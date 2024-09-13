import re
from enum import Enum
from typing import Union

from botchan.settings import DEFAULT_INTENTION
from botchan.slack.data_model import Message, MessageEvent


class MessageIntent(Enum):
    UNKNOWN = 0
    CHAT = 1
    REPORT = 2
    MRKL_AGENT = 3
    QA_INTERNET = 4
    KNOW = 5
    MIAO = 6

    @staticmethod
    def from_str(label):
        for intent in MessageIntent:
            if label == intent.name.upper():
                return intent
        raise NotImplementedError("The provided label does not match any MessageIntent")


_EMOJI_INTENT_MAP = {
    MessageIntent.CHAT: ["wave", "chat", "speech_balloon"],
    MessageIntent.KNOW: ["know", "learn", "rem"],
    MessageIntent.REPORT: ["report"],
    MessageIntent.MRKL_AGENT: ["thought", "chains", "cot"],
    MessageIntent.QA_INTERNET: ["qa"],
    MessageIntent.MIAO: ["cat"],
}

_INTENT_BY_EMOJI = {
    emoji: intent for intent, emojis in _EMOJI_INTENT_MAP.items() for emoji in emojis
}


def get_message_intent(message: Union[Message, MessageEvent]):
    for emoji in _INTENT_BY_EMOJI:
        if message.text.startswith(f":{emoji}:"):
            return _INTENT_BY_EMOJI[emoji]
    return MessageIntent.from_str(DEFAULT_INTENTION.strip().upper())


def remove_emoji_prefix(text: str) -> str:
    """
    Remove the emojie prefix from text. The emoji prefix is wrap in ':' sign
    ":shell:ABC" => "ABC"
    ":thought: what is 2 + 2?" => "what is 2 + 2?"
    """
    result = re.sub(r":.*?:", "", text)
    return result.strip()  # strip off any leading/trailing white spaces
