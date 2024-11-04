from abc import ABC, abstractmethod

from discord.message import Message

from botchan.data_model.slack import MessageEvent


class BotProxy(ABC):
    @abstractmethod
    def on_message(self, message: MessageEvent | Message) -> None:
        pass
