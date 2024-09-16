from botchan.agents.message_agent import MessageAgent
from botchan.message_intent import MessageIntent
from botchan.slack.data_model.message_event import MessageEvent

_AGENT_DESC = """A expert agent handle consultant request regarding the follow topic:
{topics_joined}
"""


class ExpertAgent(MessageAgent):
    def __init__(self) -> None:
        super().__init__()

    def process_message(self, message_event: MessageEvent) -> list[str]:
        return ["(In expert consultant mode)"]

    @property
    def description(self):
        return _AGENT_DESC.format(topics_joined="")

    @property
    def intent(self):
        return MessageIntent.EXPERT
