from abc import ABC, abstractmethod

from discord.message import Message

from botchan.data_model.slack import MessageEvent


class BotProxy(ABC):
    def handle_message(self, message: MessageEvent | Message) -> None:
        self.on_message(message=message)

    @abstractmethod
    async def on_message(self, message: MessageEvent | Message) -> None:
        pass
