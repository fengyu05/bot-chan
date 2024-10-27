from abc import ABC, abstractmethod

import structlog

from botchan.agents import MessageIntentAgent
from botchan.intent.message_intent import MessageIntent, create_intent
from botchan.slack.data_model import MessageEvent

logger = structlog.getLogger(__name__)


class IntentMatcherBase(ABC):
    intent_by_thread: dict[str, MessageIntent]
    agents: list[MessageIntentAgent]

    def __init__(
        self,
        agents: list[MessageIntentAgent],
    ) -> None:
        self.intent_by_thread = {}
        self.agents = agents

    @abstractmethod
    def parse_intent(self, text: str) -> MessageIntent:
        pass

    def match_message_intent(self, message_event: MessageEvent) -> MessageIntent:
        if message_event.thread_message_id in self.intent_by_thread:
            return self.intent_by_thread[message_event.thread_message_id]
        if not message_event.text:
            return create_intent(unknown=True)
        message_intent = self.parse_intent(message_event.text)
        logger.info("Matched intent", intent=message_intent)
        self.intent_by_thread[message_event.thread_message_id] = message_intent
        return message_intent
