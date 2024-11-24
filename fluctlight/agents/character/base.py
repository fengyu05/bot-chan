
from abc import ABC, abstractmethod

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema.messages import BaseMessage
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from fluctlight.logger import get_logger
from fluctlight.utt.timed import get_timer
from fluctlight.data_model.interface.character import Character


logger = get_logger(__name__)

timer = get_timer()






class CharacterAgent(ABC):
    config: dict
    chat_model: BaseChatModel

    @abstractmethod
    def chat(
        self,
        history: list[BaseMessage],
        user_input: str,
        character: Character,
        callbacks: list[AsyncCallbackHandler] | None = None,
        metadata: dict | None = None,
    ):
        pass

    def get_config(self):
        return self.config
