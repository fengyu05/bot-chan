from .client import create_slack_client
from .messages_fetcher import MessagesFetcher

# Shared global slack client
SLACK_CLIENT = create_slack_client()

# Shared message fetcher
SLACK_MESSAGE_FETCHER = MessagesFetcher(SLACK_CLIENT)
