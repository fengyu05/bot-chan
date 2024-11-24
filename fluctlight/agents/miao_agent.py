from fluctlight.agents.message_intent_agent import MessageIntentAgent
from fluctlight.data_model.slack.message_event import MessageEvent
from fluctlight.intent.message_intent import create_intent, MessageIntent

_AGENT_DESC = (
    """A miao agent handle the message request such as mimicking a cat voice. """
)
INTENT_KEY = "MIAO"


class MiaoAgent(MessageIntentAgent):
    def __init__(self) -> None:
        super().__init__(intent=create_intent(INTENT_KEY))

    def process_message(self, message_event: MessageEvent, message_intent: MessageIntent) -> list[str]:
        return [":cat: miao~~"]

    @property
    def description(self) -> str:
        return _AGENT_DESC
