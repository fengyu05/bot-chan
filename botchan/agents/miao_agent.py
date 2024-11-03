from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.data_model.message_event import MessageEvent
from botchan.intent.message_intent import create_intent

_AGENT_DESC = (
    """A miao agent handle the message request such as mimicking a cat voice. """
)
INTENT_KEY = "MIAO"


class MiaoAgent(MessageIntentAgent):
    def __init__(self) -> None:
        super().__init__(intent=create_intent(INTENT_KEY))

    def process_message(self, message_event: MessageEvent) -> list[str]:
        return [":cat: miao~~"]

    @property
    def description(self) -> str:
        return _AGENT_DESC
