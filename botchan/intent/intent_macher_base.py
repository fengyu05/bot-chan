from abc import ABC, abstractmethod

import structlog

from botchan.agents import MessageIntentAgent
from botchan.intent.message_intent import (
    MessageIntent,
    create_intent,
    get_message_intent_by_emoji,
)
from botchan.settings import LLM_INTENT_MATCHING
from botchan.slack.data_model import MessageEvent

logger = structlog.getLogger(__name__)


class IntentMatcherBase(ABC):
    intent_by_thread: dict[str, MessageIntent]
    agents: list[MessageIntentAgent]

    def __init__(
        self,
        agents: list[MessageIntentAgent],
        use_llm: bool = LLM_INTENT_MATCHING,
    ) -> None:
        self.intent_by_thread = {}
        self.agents = agents
        self.use_llm = use_llm

    @abstractmethod
    def parse_intent(self, message_event: MessageEvent) -> MessageIntent:
        pass

    def match_message_intent(self, message_event: MessageEvent) -> MessageIntent:
        if message_event.thread_message_id in self.intent_by_thread:
            return self.intent_by_thread[message_event.thread_message_id]
        if self.use_llm:
            message_intent = self.parse_intent()
        else:
            if message_event.text:
                message_intent = get_message_intent_by_emoji(message_event.text)
            else:
                message_intent = create_intent("unkown")
        logger.info("Matched intent", intent=message_intent)
        self.intent_by_thread[message_event.thread_message_id] = message_intent
        return message_intent
