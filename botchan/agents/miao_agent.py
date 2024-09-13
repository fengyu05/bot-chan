from botchan.agents.message_agent import MessageAgent
from botchan.message_intent import MessageIntent
from botchan.slack.data_model.message_event import MessageEvent

_AGENT_DESC = """A miao agent handle the message request such as mimicking a cat voice.

For examples:
"Can you play a cat?",
"Pretent you are a cat, what do you say?",
"You are a cat now!",
"Response like you are a kitty"
"""


class MiaoAgent(MessageAgent):
    def __init__(self) -> None:
        super().__init__()

    def process_message(self, message_event: MessageEvent) -> list[str]:
        return [":cat: miao~~"]

    @property
    def description(self):
        return _AGENT_DESC

    @property
    def intent(self):
        return MessageIntent.MIAO
