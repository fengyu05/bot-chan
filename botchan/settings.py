import os
from typing import Any, Optional

from botchan.constants import GPT_4O


def config_default(key: str, default_value: Optional[Any] = None) -> Any:
    return os.environ.get(key, default_value)


def config_default_float(key: str, default_value: Any = 0.0) -> float:
    return float(os.environ.get(key, default_value))


def config_default_bool(key: str, default_value: bool = False) -> bool:
    return bool(os.environ.get(key, default_value))


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

# Whether to use LLM to match message intent
LLM_INTENT_MATCHING = config_default_bool("LLM_INTENT_MATCHING", True)


# Default tmp path
TMP_PATH = config_default("TMP", "/tmp/")

# Embedding base retrival sim score threshold
EMBEDDING_SIM_SCORE_THESHOLD = config_default_float("EMBEDDING_SIM_SCORE_THESHOLD", 0.5)

# Slack transcrition callback waiting time
SLACK_TRANSCRIBE_WAIT_SEC = config_default_float("SLACK_TRANSCRIBE_WAIT_SEC", 10)
