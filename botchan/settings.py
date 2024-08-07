import os

from botchan.constants import GPT_4O

# App config
ENV = os.environ.get("ENV", "dev")
APP_NAME = os.environ.get("APP_NAME", "botchan")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Bot config
BOT_NAME = os.environ.get("BOT_NAME", APP_NAME)

# Slack credential
SLACK_APP_OAUTH_TOKENS_FOR_WS = os.environ.get("SLACK_APP_OAUTH_TOKENS_FOR_WS")
SLACK_APP_LEVEL_TOKEN = os.environ.get("SLACK_APP_LEVEL_TOKEN")

# OPENAI API KEY
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OPENAI GPT MODEL ID
OPENAI_GPT_MODEL_ID = os.environ.get("OPENAI_GPT_MODEL_ID", GPT_4O)

# Default intention to use without mapping
DEFAULT_INTENTION = os.environ.get("DEFAULT_INTENTION", "CHAT")

# ChAT_MODE, SIMPLE|RAG
CHAT_MODE = os.environ.get("CHAT_MODE", "SIMPLE")

# SERPAPI API KEY, optional
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", None)

# NEWS API KEY, optional
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", None)

## Below is for knowledge indexing

# Knowledge folder
KNOWLEDGE_FOLDER = os.environ.get("KNOWLEDGE_FOLDER", "/doc2index/test")

# Accept knowledge file extention
KNOWLEDGE_ACCEPT_PATTERN = [".txt", ".md"]

# Default tools to load
MARK_LOAD_TOOLS = os.environ.get(
    "DEFAULT_LOAD_TOOLS", "llm-math,wikipedia,arxiv"
).split(",")

# Default tmp path
TMP_PATH = os.environ.get("TMP", "/tmp/")

# Embedding base retrival sim score threshold
EMBEDDING_SIM_SCORE_THESHOLD = float(
    os.environ.get("EMBEDDING_SIM_SCORE_THESHOLD", 0.4)
)

## End of knowledge indexing setting
