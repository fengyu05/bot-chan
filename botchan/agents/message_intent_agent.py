from abc import abstractmethod
from typing import Any

import structlog

from botchan.message_intent import MessageIntent
from botchan.slack.data_model import MessageEvent
from botchan.task import Task

logger = structlog.getLogger(__name__)


class MessageIntentAgent(Task):
    """
    This class provides a framework for processing messages by defining
    abstract methods that must be implemented in subclasses. It offers
    mechanisms to process messages, check if a certain intent should be
    processed, and includes properties for the agent's name, intent, and
    description.

    Methods:
        __init__(): Initializes the MessageIntentAgent object.
        process(*args: Any, **kwds: Any) -> Any: Processes a message event.
        process_message(message_event: MessageEvent) -> list[str]: Abstract method to process a message event.
        should_process(*args: Any, **kwds: Any) -> bool: Determines if the intent should be processed based on input arguments.

    Properties:
        name (str): Returns the name of the agent.
        intent (MessageIntent): Abstract property representing the intent of the agent.
        description (str): Abstract property describing the agent's function.
    """

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

    def should_process(
        self, *args: Any, **kwds: Any
    ) -> bool:  # pylint: disable=unused-argument
        message_intent: MessageIntent = self._require_input(
            kwargs=kwds, key="message_intent"
        )
        return message_intent == self.intent

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    @abstractmethod
    def intent(self) -> MessageIntent:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass
