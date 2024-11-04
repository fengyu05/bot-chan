from abc import ABC, abstractmethod

from botchan.data_model import MessageEvent


class BotProxy(ABC):
    @abstractmethod
    def receive_message(self, message_event: MessageEvent) -> None:
        pass
