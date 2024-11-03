from abc import ABC, abstractmethod

from botchan.data_model import MessageEvent
from botchan.intent.intent_agent import IntentAgent
from botchan.intent.message_intent import (
    DEFAULT_CHAT_INTENT,
    UNKNOWN_INTENT,
    MessageIntent,
    get_message_intent_by_emoji,
)
from botchan.logger import get_logger
from botchan.settings import LLM_INTENT_MATCHING

logger = get_logger(__name__)


class IntentMatcher(ABC):
    intent_by_thread: dict[str, MessageIntent]
    agents: list[IntentAgent]

    def __init__(
        self,
        agents: list[IntentAgent],
    ) -> None:
        self.intent_by_thread = {}
        self.agents = agents

    @abstractmethod
    def parse_intent(self, text: str) -> MessageIntent:
        pass

    def match_message_intent(self, message_event: MessageEvent) -> MessageIntent:
        """
        Determines the intent of a given message event.

        This method attempts to match the intent based on the thread message ID or
        the text content of the message. It uses various strategies such as emoji detection
        and potentially large language model (LLM) based matching if enabled.

        Args:
            message_event (MessageEvent): The message event object containing details like
                                        thread message ID and text of the message.

        Returns:
            MessageIntent: The determined intent of the message, either retrieved from stored
                        intents by thread, derived from the message text, or defaults.
        """
        if message_event.thread_message_id in self.intent_by_thread:
            return self.intent_by_thread[message_event.thread_message_id]
        if not message_event.text:
            return UNKNOWN_INTENT
        message_intent = get_message_intent_by_emoji(message_event.text)
        if message_intent.unknown:
            if LLM_INTENT_MATCHING:
                message_intent = self.parse_intent(message_event.text)
            else:
                message_intent = DEFAULT_CHAT_INTENT

        logger.info("Matched intent", intent=message_intent)
        self.intent_by_thread[message_event.thread_message_id] = message_intent
        return message_intent
