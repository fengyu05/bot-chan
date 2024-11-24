from abc import ABC, abstractmethod

from discord.message import Message

from fluctlight.data_model.slack import MessageEvent


class BotProxy(ABC):
    @abstractmethod
    async def on_message(self, message: MessageEvent | Message) -> None:
        pass
