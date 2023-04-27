from typing import List

from pydantic import BaseModel

from .message_intent import MessageIntent

_DESCRIPTION = "description"
_TEMPLATE = "template"
_INPUT_VARIABLES = "input_variables"
_INPUT_KEY = "input_key"
_MEMORY_BUFFER = "memory_buffer"

# Yor bot personalization config here.
_ALL_PROMPT = {
    MessageIntent.CHAT: {
        _DESCRIPTION: "For default natural conversation.",
        _TEMPLATE: """{bot_name} is a Chabot application developed by Z that is designed to help you with a variety of tasks.
        {bot_name} can engage in natural-sounding conversations and provide you with relevant and helpful responses. {bot_name} is here to make your life easier and help you get things done quickly and efficiently.

{history}
Human: {human_input}
{bot_name} :""",
        _INPUT_VARIABLES: ["history", "human_input", "bot_name"],
        _INPUT_KEY: "human_input",
        _MEMORY_BUFFER: 10,
    },
}


class Prompt(BaseModel):
    description: str
    template: str
    input_variables: List[str]
    input_key: str
    memory_buffer: int

    class Config:
        use_enum_values = True

    @classmethod
    def from_intent(cls, intent: MessageIntent) -> "Prompt":
        prompt_dict = Prompt.get_prompt_dict(intent)
        return cls(**prompt_dict)

    @staticmethod
    def get_prompt_dict(intent: MessageIntent) -> dict:
        return {
            "description": _ALL_PROMPT[intent][_DESCRIPTION],
            "template": _ALL_PROMPT[intent][_TEMPLATE],
            "input_variables": _ALL_PROMPT[intent][_INPUT_VARIABLES],
            "input_key": _ALL_PROMPT[intent][_INPUT_KEY],
            "memory_buffer": _ALL_PROMPT[intent][_MEMORY_BUFFER],
        }
