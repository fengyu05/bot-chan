# pylint: disable=unnecessary-lambda
# pylint: disable=unused-argument
from functools import cached_property
from typing import Union

import structlog
from slack_sdk import WebClient

from botchan.agents import Agent
from botchan.agents.miao_agent import MiaoAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.constants import GPT_4O_MINI
from botchan.message_intent import MessageIntent, get_message_intent
from botchan.openai import CLIENT as openai_client
from botchan.openai.chat_utils import simple_assistant
from botchan.settings import LLM_INTENT_MATCHING
from botchan.slack import auth as slack_auth
from botchan.slack import chat as slack_chat
from botchan.slack import reaction as slack_reaction
from botchan.slack.data_model import (
    MessageCreateEvent,
    MessageEvent,
    MessageFileShareEvent,
)
from botchan.slack.messages_fetcher import MessagesFetcher

logger = structlog.getLogger(__name__)


class MessageMultiIntentAgent:
    slack_client: WebClient
    fetcher: MessagesFetcher
    bot_user_id: str
    agents: list[Agent]

    def __init__(self, slack_client: WebClient):
        self.slack_client = slack_client
        self.fetcher = MessagesFetcher(self.slack_client)
        self.bot_user_id = slack_auth.get_bot_user_id(self.slack_client)

        self.agents = [
            OpenAiChatAgent(),  ## Handle simple chat
            MiaoAgent(),
        ]

    def _should_reply(self, message_event: MessageCreateEvent) -> bool:
        return message_event.channel_type == "im" or message_event.is_user_mentioned(
            self.bot_user_id
        )

    def receive_message(
        self, message_event: Union[MessageCreateEvent, MessageFileShareEvent]
    ) -> None:
        if self._should_reply(message_event):  # IM or mentioned
            slack_reaction.add_reaction(
                client=self.slack_client, event=message_event, reaction_name="eyes"
            )
            message_intent = self.match_message_intent(message_event=message_event)
            for agent in self.agents:
                msgs = agent(message_event=message_event, message_intent=message_intent)
                if msgs is None:  ## agent didn't process this intent
                    continue
                for msg in msgs:
                    slack_chat.reply_to_message(self.slack_client, message_event, msg)

    def match_message_intent(self, message_event: MessageEvent) -> MessageIntent:
        if LLM_INTENT_MATCHING:
            prompt = self.match_intent_prompt(message=message_event.text)
            logger.info("LLM intent matching", prompt=prompt)
            text = simple_assistant(model_id=GPT_4O_MINI, prompt=prompt)
            logger.info("Matched intent", intent=text)
            return MessageIntent.from_str(text.upper())
        else:
            return get_message_intent(message=message_event)

    def match_intent_prompt(self, message: str) -> str:
        return f"""Help match the message intent to the following agents.
        -------------------
        {self.joined_agents_description}
        -------------------
        For example:

        user_message: "Can you play a cat?"
        output: MIAO

        If you can now detech a good match, use default intent 'CHAT'.
        Output text should only be one of the following enum in uppercase.
        ---------------------
        {self.joined_all_intents}
        --------------------
        user_message: {message}
        output:
        """

    @cached_property
    def joined_agents_description(self) -> str:
        result = ""
        for agent in self.agents:
            result += f"{agent.intent.name}: {agent.description}\n"
        return result

    @cached_property
    def joined_all_intents(self) -> str:
        result = ", ".join([intent.name for intent in MessageIntent])
        return result
