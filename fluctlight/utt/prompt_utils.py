from typing import Any

from jinja2 import Template
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from fluctlight.logger import get_logger
from fluctlight.settings import DEBUG_MODE

logger = get_logger(__name__)


def construct_system_prompt(prompt: str, context: dict[str, Any]) -> ChatPromptTemplate:
    template = Template(prompt)
    text = template.render(context)
    if DEBUG_MODE:
        logger.debug("construct system prompt", text=text)
    return ChatPromptTemplate.from_messages(
        [
            ("system", text),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
