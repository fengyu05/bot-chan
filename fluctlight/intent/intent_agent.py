from abc import ABC, abstractmethod

from fluctlight.intent.message_intent import MessageIntent


class IntentAgent(ABC):
    @property
    @abstractmethod
    def intent(self) -> MessageIntent:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def llm_matchable(self) -> str:
        pass
