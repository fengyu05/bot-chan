from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.intent.message_intent import create_intent
from botchan.slack.data_model.message_event import MessageEvent

_AGENT_DESC = """A miao agent handle the message request such as mimicking a cat voice.

For examples:
"Can you play a cat?",
"Pretent you are a cat, what do you say?",
"You are a cat now!",
"Response like you are a kitty"
"""

INTENT_KEY = "MIAO"


class MiaoAgent(MessageIntentAgent):
    def __init__(self) -> None:
        super().__init__(intent=create_intent(INTENT_KEY))

    def process_message(self, message_event: MessageEvent) -> list[str]:
        return [":cat: miao~~"]

    @property
    def description(self) -> str:
        return _AGENT_DESC
