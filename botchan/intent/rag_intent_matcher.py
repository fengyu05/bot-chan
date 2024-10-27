import json
import operator
from functools import cached_property
from typing import Annotated, List, Sequence

import structlog
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_fireworks import ChatFireworks
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from pydantic import ValidationError
from typing_extensions import TypedDict

from botchan.agents import MessageIntentAgent
from botchan.chain.prompt_utils import construct_system_prompt
from botchan.constants import FIREWORKS_MIXTRAL_7B
from botchan.intent.intent_macher_base import IntentMatcherBase
from botchan.intent.message_intent import IntentCandidate, MessageIntent, create_intent

logger = structlog.getLogger(__name__)


_MATCH_PROMPT = """
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

_REFLECTION_PROMPT = """
Analyze the JSON payload to refine the intent candidate result. Follow these steps:

1. Check if `IntentName1` exactly matches an entry in the `intent_list`.
2. If `IntentName1` does not match, attempt to correct it to the nearest valid entry in `intent_list`.
3. When `IntentName1` cannot be recognized or corrected, utilize `IntentName2` instead.
4. Remove any unnecessary escape characters from the input.
5. Output only the final, adjusted `intent_name`.

Input: JSON payload as provided
Output: Singular refined intent name (do not include additional text)
Intent list:
-------------
{intent_choices}
"""


class GraphState(TypedDict):
    messages: Sequence[BaseMessage]
    intent_candidate: IntentCandidate | None  # LLM generation
    final_intent: str | None  # Binary decision to run web search


class RagIntentMatcher(IntentMatcherBase):

    def __init__(
        self,
        agents: list[MessageIntentAgent],
        model_id: str = FIREWORKS_MIXTRAL_7B,
        max_tokens: int = 32768,
    ) -> None:
        super().__init__(
            agents=agents,
        )
        self.llm = ChatFireworks(model=model_id, max_tokens=max_tokens)
        self.match_intent_chain = (
            construct_system_prompt(
                prompt=_MATCH_PROMPT,
                context={"intent_list": self.construct_intent_list},
            )
            | self.llm
        )
        self.refine_intent_chain = (
            construct_system_prompt(
                prompt=_REFLECTION_PROMPT,
                context={"intent_choices": ",".join(self.intent_keyset)},
            )
            | self.llm
        )

        # Build graph
        self.graph = self.build_graph()

    def build_graph(self) -> CompiledStateGraph:
        workflow = StateGraph(GraphState)

        def match_intent(state: GraphState) -> GraphState:
            messages = state["messages"]
            question = messages[0].content
            assert isinstance(question, str), "input question must be text"
            output = self.match_intent_chain.invoke(
                {"messages": [HumanMessage(content=question)]}
            )
            logger.info("match_intent", output=output)
            assert isinstance(output.content, str), "expect output.content to be text"
            intent_candidate = self.parse_output_json(output.content)
            assert intent_candidate, "intent_candidate must present"
            return GraphState(
                messages=messages,
                intent_candidate=intent_candidate,
                final_intent=None,
            )

        def refine_intent(state: GraphState) -> GraphState:
            messages = state["messages"]
            question = messages[0].content
            intent_candidate = state["intent_candidate"]
            assert intent_candidate, "intent_candidate must present"
            output = self.refine_intent_chain.invoke(
                {
                    "messages": [
                        HumanMessage(content=question),
                        AIMessage(content=intent_candidate.model_dump_json()),
                    ]
                }
            )
            logger.info("refine_intent", output=output)
            assert isinstance(output.content, str), "expect output.content to be text"
            return GraphState(
                messages=messages,
                intent_candidate=intent_candidate,
                final_intent=output.content,
            )

        def need_refine(state: GraphState) -> str:
            intent_candidate = state["intent_candidate"]
            assert intent_candidate, "intent_candidate must present"
            if intent_candidate.IntentName1 in self.intent_keyset:
                return "NO"
            return "YES"

        # Define the nodes
        workflow.add_node("match_intent", match_intent)
        workflow.add_node("refine_intent", refine_intent)
        # Add edge
        workflow.add_edge(START, "match_intent")
        workflow.add_conditional_edges(
            "match_intent",
            need_refine,
            {
                "NO": END,
                "YES": "refine_intent",
            },
        )
        workflow.add_edge("refine_intent", END)
        # Compile
        return workflow.compile()

    def parse_intent(self, text: str) -> MessageIntent:
        events = self.graph.stream(
            {
                "messages": [HumanMessage(content=text)],
            },
            # Maximum number of steps to take in the graph
            {"recursion_limit": 10},
        )

        logger.info("all_event", events=events)

        for x in events:
            logger.info("event", x=x)

        return MessageIntent(key="unkown")

    @cached_property
    def construct_intent_list(self) -> str:
        return "\n---\n".join(
            [
                f"{agent.intent.key}: {agent.description}"
                for _, agent in enumerate(self.agents)
            ]
        )

    @cached_property
    def intent_keyset(self) -> set[str]:
        return {agent.intent.key for _, agent in enumerate(self.agents)}

    def parse_output_json(self, text: str) -> IntentCandidate | None:
        try:
            data = json.loads(text)
            return IntentCandidate(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error parsing JSON: {e}")
            return None
