import os

# App config
ENV = os.environ.get("ENV", "dev")
APP_NAME = os.environ.get("APP_NAME", "botchan")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Bot config
BOT_NAME = "Botchan"

# Slack credential
SLACK_APP_OAUTH_TOKENS_FOR_WS = os.environ.get("SLACK_APP_OAUTH_TOKENS_FOR_WS")
SLACK_APP_LEVEL_TOKEN = os.environ.get("SLACK_APP_LEVEL_TOKEN")

# OPENAI API KEY
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OPENAI GPT MODEL ID
OPENAI_GPT_MODEL_ID = os.environ.get("OPENAI_GPT_MODEL_ID", "gpt-3.5-turbo")

# SERPAPI API KEY
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", None)

# NEWS API KEY
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", None)
