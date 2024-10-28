from abc import ABC, abstractmethod

from botchan.intent.message_intent import MessageIntent


class IntentAgent(ABC):
    @property
    @abstractmethod
    def intent(self) -> MessageIntent:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass
