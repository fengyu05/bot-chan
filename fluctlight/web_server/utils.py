import asyncio
from dataclasses import field
from typing import Optional, TypedDict

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic.dataclasses import dataclass

from sqlalchemy.orm import Session

from fluctlight.database.models.interaction import Interaction
from fluctlight.logger import get_logger


logger = get_logger(__name__)





@dataclass
class ConversationHistory:
    system_prompt: str = ""
    user: list[str] = field(default_factory=list)
    ai: list[str] = field(default_factory=list)

    def __iter__(self):
        yield self.system_prompt
        for user_message, ai_message in zip(self.user, self.ai):
            yield user_message
            yield ai_message

    def load_from_db(self, session_id: str, db: Session):
        conversations = db.query(Interaction).filter(Interaction.session_id == session_id).all()
        for conversation in conversations:
            self.user.append(conversation.client_message_unicode)  # type: ignore
            self.ai.append(conversation.server_message_unicode)  # type: ignore


def build_history(conversation_history: ConversationHistory) -> list[BaseMessage]:
    history = []
    for i, message in enumerate(conversation_history):
        if i == 0:
            history.append(SystemMessage(content=message))
        elif i % 2 == 0:
            history.append(AIMessage(content=message))
        else:
            history.append(HumanMessage(content=message))
    return history


@dataclass
class TranscriptSlice:
    id: str
    audio_id: str
    start: float
    end: float
    speaker_id: str
    text: str


@dataclass
class Transcript:
    id: str
    audio_bytes: bytes
    slices: list[TranscriptSlice]
    timestamp: float
    duration: float


class DiarizedSingleSegment(TypedDict):
    start: float
    end: float
    text: str
    speaker: str


class SingleWordSegment(TypedDict):
    word: str
    start: float
    end: float
    score: float


class WhisperXResponse(TypedDict):
    segments: list[DiarizedSingleSegment]
    language: str
    word_segments: list[SingleWordSegment]



def task_done_callback(task: asyncio.Task):
    exception = task.exception()
    if exception:
        logger.error(f"Error in task {task.get_name()}: {exception}")