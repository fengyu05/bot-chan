from abc import abstractmethod
from typing import Any

import structlog

from botchan.message_intent import MessageIntent
from botchan.slack.data_model import MessageEvent

from .agent_base import Agent

logger = structlog.getLogger(__name__)


class MessageAgent(Agent):
    """MessageAgent is the abstract class to handle process on message."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any, **kwds: Any) -> Any:
        message_event: MessageEvent = self._require_input(
            kwargs=kwds, key="message_event"
        )
        msgs = self.process_message(message_event)
        logger.debug("agent process messult result", agent=self.name, msg=msgs)
        return msgs

    @abstractmethod
    def process_message(self, message_event: MessageEvent) -> list[str]:
        pass
