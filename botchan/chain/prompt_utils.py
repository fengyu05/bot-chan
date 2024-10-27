import structlog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

logger = structlog.getLogger(__name__)


def construct_system_prompt(prompt: str, context: dict[str, str]) -> ChatPromptTemplate:
    text = prompt.format(**context)
    logger.debug("construct system prompt", text=text)
    return ChatPromptTemplate.from_messages(
        [
            ("system", text),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
