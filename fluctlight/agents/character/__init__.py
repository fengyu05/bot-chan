from .base import CharacterAgent
from .openai_character_agent import OpenAICharacterAgent
from fluctlight.constants import GPT_4O


def create_default_character_agent() -> CharacterAgent:
    return OpenAICharacterAgent(
        model=GPT_4O
    )