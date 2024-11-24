from abc import ABC, abstractmethod
from functools import cache
from fluctlight.data_model.interface import IMessage
from fluctlight.intent.intent_agent import IntentAgent
from fluctlight.intent.message_intent import (
    DEFAULT_CHAT_INTENT,
    UNKNOWN_INTENT,
    MessageIntent,
    get_message_intent_by_emoji,
    get_leading_emoji,
)
from fluctlight.logger import get_logger
from fluctlight.settings import LLM_INTENT_MATCHING, CHAR_AGENT_MATCHING
from fluctlight.agent_catalog.catalog_manager import get_catalog_manager
logger = get_logger(__name__)


class IntentMatcher(ABC):
    intent_by_thread: dict[str, MessageIntent]
    agents: list[IntentAgent]
    _chars_map: dict[str, str] | None = None

    def __init__(
        self,
        agents: list[IntentAgent],
    ) -> None:
        self.intent_by_thread = {}
        self.agents = agents
        self.catalog_manager = get_catalog_manager()

    @abstractmethod
    def parse_intent(self, text: str) -> MessageIntent:
        pass

    def match_message_intent(self, message: IMessage) -> MessageIntent:
        """
        Determines the intent of a message using thread ID or text analysis.

        Args:
            message (IMessage): The message object to analyze.

        Returns:
            MessageIntent: The detected message intent.
        """
        if message.thread_message_id in self.intent_by_thread:
            return self.intent_by_thread[message.thread_message_id]
        
        if not message.text:
            message_intent = DEFAULT_CHAT_INTENT
        else:
            message_intent = get_message_intent_by_emoji(message.text)
            if CHAR_AGENT_MATCHING and message_intent.unknown:
                message_intent = self.get_char_agent_intent(message.text)
            if LLM_INTENT_MATCHING and message_intent.unknown:
                message_intent = self.parse_intent(message.text)
        
        if message_intent.unknown:
            message_intent = DEFAULT_CHAT_INTENT

        logger.info("Matched intent", intent=message_intent)
        self.intent_by_thread[message.thread_message_id] = message_intent
        return message_intent

    def get_char_emoji_map(self) -> dict[str, str]:
        if self._chars_map is None:
            chars_map = {}
            for char_id, character in self.catalog_manager.characters.items():
                chars_map[char_id] = char_id
                chars_map[character.name] = char_id
            self._chars_map = chars_map
        return self._chars_map 

    def get_char_agent_intent(self, text: str) -> MessageIntent:
        emoji = get_leading_emoji(text)
        chars_map = self.get_char_emoji_map()
        if emoji in chars_map:
            return MessageIntent(
                key="CHAR",
                metadata={
                    "char_id": chars_map[emoji]
                }
            )
        else:
            return UNKNOWN_INTENT