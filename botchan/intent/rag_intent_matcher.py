import structlog

from botchan.agents import MessageIntentAgent
from botchan.constants import FIREWORKS_MIXTRAL_22B
from botchan.intent.intent_macher_base import IntentMatcherBase
from botchan.intent.message_intent import MessageIntent, create_intent
from botchan.settings import LLM_INTENT_MATCHING
from botchan.slack.data_model import MessageEvent

logger = structlog.getLogger(__name__)


class RagIntentMatcher(IntentMatcherBase):

    def __init__(
        self,
        agents: list[MessageIntentAgent],
        use_llm: bool = LLM_INTENT_MATCHING,
    ) -> None:
        super().__init__(
            use_llm=use_llm,
            agents=agents,
        )

    def parse_intent(self, message_event: MessageEvent) -> MessageIntent:
        message_intent = create_intent("unknown")
        return message_intent
