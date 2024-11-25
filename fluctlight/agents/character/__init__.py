from fluctlight.constants import GPT_4O

from .base import CharacterAgent
from .openai_character_agent import OpenAICharacterAgent


def create_default_character_agent() -> CharacterAgent:
    return OpenAICharacterAgent(model=GPT_4O)
