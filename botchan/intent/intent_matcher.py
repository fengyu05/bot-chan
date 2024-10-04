import re
import string
from functools import cached_property

import structlog

from botchan.agents import MessageIntentAgent
from botchan.constants import GPT_4O_MINI
from botchan.intent.message_intent import (
    MessageIntent,
    create_intent,
    get_message_intent_by_emoji,
)
from botchan.open.chat_utils import simple_assistant, simple_assistant_with_struct_ouput
from botchan.settings import LLM_INTENT_MATCHING
from botchan.slack.data_model import MessageEvent

logger = structlog.getLogger(__name__)


class IntentMatcher:
    intent_by_thread: dict[str, MessageIntent]
    agents: list[MessageIntentAgent]

    def __init__(
        self,
        agents: list[MessageIntentAgent],
        use_llm: bool = LLM_INTENT_MATCHING,
        use_strcuture_output: bool = False,
    ) -> None:
        self.use_llm = use_llm
        self.use_structure_output = use_strcuture_output
        self.intent_by_thread = {}
        self.agents = agents

    def match_message_intent(self, message_event: MessageEvent) -> MessageIntent:
        if message_event.thread_message_id in self.intent_by_thread:
            return self.intent_by_thread[message_event.thread_message_id]

        if self.use_llm:
            if self.use_structure_output:
                prompt = self.match_intent_prompt_structure(message=message_event.text)
                logger.debug("LLM intent matching", prompt=prompt)
                message_intent = simple_assistant_with_struct_ouput(
                    model_id=GPT_4O_MINI, prompt=prompt, output_schema=MessageIntent
                )
            else:
                prompt = self.match_intent_prompt_non_structure(
                    message=message_event.text
                )
                logger.debug("LLM intent matching", prompt=prompt)
                selected_text = simple_assistant(model_id=GPT_4O_MINI, prompt=prompt)
                logger.debug("LLM intent matching selected_text", selected_text=selected_text)
                message_intent = self.get_message_intent_from_index_text(selected_text)
        else:
            message_intent = get_message_intent_by_emoji(message_event.text)
        logger.info("Matched intent", intent=message_intent)
        self.intent_by_thread[message_event.thread_message_id] = message_intent
        return message_intent

    def get_message_intent_from_index_text(self, text: str) -> MessageIntent:
        try:
            # Remove non-numeric characters from the text
            numeric_text = re.sub(r'\D', '', text)
            
            # Attempt to convert the sanitized text to an integer
            idx = int(numeric_text)
            return self.agents[idx].intent
        except ValueError:
            return create_intent("UNKNOWN")

    def match_intent_prompt_structure(self, message: str) -> str:
        return f"""Select one of the below task based on the user message. 
-----------
{self.joined_agents_description_for_structure}
You may only use the option from the below.
If you can not detect a good match, use defaut task: Type='CHAT', Key=None.
{self.joined_agents_selection}
-----------------------
user_message: {message}
output:"""

    @cached_property
    def joined_agents_description_for_structure(self) -> str:
        result = "".join(
            [
                f"Type={agent.intent.type.name}, key={agent.intent.key}: {agent.description} \n---\n"
                for agent in self.agents
            ]
        )
        return result

    @cached_property
    def joined_agents_selection(self) -> str:
        return "".join(
            [
                f"Type={agent.intent.type.name}, key={agent.intent.key} \n---\n"
                for agent in self.agents
            ]
        )

    def match_intent_prompt_non_structure(self, message: str) -> str:
        return f"""Select one of the below task based on the user message. 
-----------
{self.joined_agents_description_list}
You may only use the option from the below. Output format should only include one number for the above tasks.
If you can not detect a good match, use defaut task: 0)
-----------------------
user_message: {message}
output:"""

    @cached_property
    def joined_agents_description_list(self) -> str:
        result = "".join(
            [
                f"{i}: {agent.description} \n---\n"
                for i, agent in enumerate(self.agents)
            ]
        )
        return result
