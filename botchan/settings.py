import os
from typing import Any, Optional

from botchan.constants import GPT_4O


def config_default(key: str, value: Optional[Any] = None) -> Any:
    return os.environ.get(key, value)


def config_default_float(key: str, value: Any = 0.0) -> float:
    return float(os.environ.get(key, value))


# App config
ENV = config_default("ENV", "dev")
APP_NAME = config_default("APP_NAME", "botchan")
LOG_LEVEL = config_default("LOG_LEVEL", "INFO")

# Bot config
BOT_NAME = config_default("BOT_NAME", APP_NAME)

# Slack credential
SLACK_APP_OAUTH_TOKENS_FOR_WS = config_default("SLACK_APP_OAUTH_TOKENS_FOR_WS")
SLACK_APP_LEVEL_TOKEN = config_default("SLACK_APP_LEVEL_TOKEN")

# OPENAI API KEY
OPENAI_API_KEY = config_default("OPENAI_API_KEY")

# OPENAI GPT MODEL ID
OPENAI_GPT_MODEL_ID = config_default("OPENAI_GPT_MODEL_ID", GPT_4O)

# Default intention to use without mapping
DEFAULT_INTENTION = config_default("DEFAULT_INTENTION", "CHAT")

# ChAT_MODE, SIMPLE|RAG
CHAT_MODE = config_default("CHAT_MODE", "SIMPLE")

# SERPAPI API KEY, optional
SERPAPI_API_KEY = config_default("SERPAPI_API_KEY")

# NEWS API KEY, optional
NEWS_API_KEY = config_default("NEWS_API_KEY")

## Below is for knowledge indexing

# Knowledge folder
KNOWLEDGE_FOLDER = config_default("KNOWLEDGE_FOLDER", "/doc2index/test")

# Accept knowledge file extention
KNOWLEDGE_ACCEPT_PATTERN = [".txt", ".md"]

# Default tools to load
MARK_LOAD_TOOLS = config_default(
    "DEFAULT_LOAD_TOOLS", "llm-math,wikipedia,arxiv"
).split(",")

# Default tmp path
TMP_PATH = config_default("TMP", "/tmp/")

# Embedding base retrival sim score threshold
EMBEDDING_SIM_SCORE_THESHOLD = config_default_float("EMBEDDING_SIM_SCORE_THESHOLD", 0.4)

# Slack transcrition callback waiting time
SLACK_TRANSCRIBE_WAIT_SEC = config_default_float("SLACK_TRANSCRIBE_WAIT_SEC", 10)

## End of knowledge indexing setting
