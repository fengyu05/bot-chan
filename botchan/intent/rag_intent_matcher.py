import json
from typing import Annotated, List, Sequence

import structlog
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_fireworks import ChatFireworks
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import ValidationError
from typing_extensions import TypedDict

from botchan.agents import MessageIntentAgent
from botchan.constants import FIREWORKS_MIXTRAL_7B
from botchan.intent.intent_macher_base import IntentMatcherBase
from botchan.intent.message_intent import IntentCandidate, MessageIntent, create_intent
from botchan.settings import LLM_INTENT_MATCHING

logger = structlog.getLogger(__name__)


_PROMPT = """
The system will determine the most appropriate intents from a user message using the following steps:

1. Extract key phrases indicating the user's need or desired action.
2. Identify if the message relates to retail, photo, pharmacy departments, or is vague.
3. Compare these key phrases with intent descriptions.
4. Find which intents best align with extracted phrases.
5. Evaluate how well each intent matches the user's goals.
6. Rank and select the top two relevant intents from the list.

Intent list:
-------------
{intent_list}

Generate a JSON output as follows, please only ouput the json, not including other text.
No need to escape underscore sign in the json payload.
    
```json

    "CustomerUnderstanding": "System's interpretation of the message.",
    "IntentName1": "Primary intent matching the user's need.",
    "IntentName2": "Secondary intent somewhat matching the need.",
    "IntentClarification": "Explanation of chosen intents' relevance."
```
"""


class State(TypedDict):
    messages: Annotated[list, add_messages]


class RagIntentMatcher(IntentMatcherBase):

    def __init__(
        self,
        agents: list[MessageIntentAgent],
        use_llm: bool = LLM_INTENT_MATCHING,
        model_id: str = FIREWORKS_MIXTRAL_7B,
        max_tokens: int = 32768,
    ) -> None:
        super().__init__(
            use_llm=use_llm,
            agents=agents,
        )
        system_instruction_text = self.construct_prompt(agents)
        logger.debug("system instruction text", text=system_instruction_text)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_instruction_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        self.llm = ChatFireworks(model=model_id, max_tokens=max_tokens)
        self.match_intent = prompt | self.llm

    def parse_intent(self, text: str) -> MessageIntent:
        request = HumanMessage(content=text)
        output = self.match_intent.invoke({"messages": [request]})
        logger.info("parse_intent", output=output)

        assert isinstance(output.content, str), "expect output.content to be text"
        intent_candidate = self.parse_output_json(output.content)

        if not intent_candidate:
            return create_intent(unknown=True)

        return MessageIntent(key=intent_candidate.IntentName1)

    def construct_prompt(self, agents: list[MessageIntentAgent]) -> str:
        return _PROMPT.format(
            intent_list="\n---\n".join(
                [
                    f"{agent.intent.key}: {agent.description}"
                    for i, agent in enumerate(agents)
                ]
            )
        )

    def parse_output_json(self, text: str) -> IntentCandidate | None:
        try:
            data = json.loads(text)
            return IntentCandidate(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error parsing JSON: {e}")
            return None
