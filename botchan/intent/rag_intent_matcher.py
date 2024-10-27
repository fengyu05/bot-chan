import json
from functools import cached_property

import structlog
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_fireworks import ChatFireworks
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import ValidationError
from typing_extensions import TypedDict

from botchan.agents import MessageIntentAgent
from botchan.chain.prompt_utils import construct_system_prompt
from botchan.constants import FIREWORKS_MIXTRAL_22B
from botchan.intent.intent_candidate import (
    EXAMPLE_INTENT_CANDIDATE,
    IntentCandidate,
    parse_intent_candidate_json,
)
from botchan.intent.intent_macher_base import IntentMatcher
from botchan.intent.message_intent import MessageIntent, create_intent

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
{{intent_list}}

Output: Generate a JSON in a single line format with the following fields.
    "understanding": "System's interpretation of the message.",
    "intent_key_primary": "Primary intent matching the user's need.",
    "intent_key_secondary": "Secondary intent somewhat matching the need."
-----------------------
Example output format:
{{json_example_payload}}
"""

_REFLECTION_PROMPT = """
Analyze the JSON payload to refine the intent candidate result. Follow these steps:

1. Check if `intent_key_primary` exactly matches an entry in the `intent_list`.
2. If `intent_key_primary` does not match, attempt to correct it to the nearest valid entry in `intent_list`.
3. When `intent_key_primary` cannot be recognized or corrected, utilize `intent_key_secondary` instead.
4. Remove any unnecessary escape characters from the input.
5. Output only the final, adjusted `intent_name`.

Intent list:
-------------
{{intent_choices}}

Output: Singular refined intent name selected from the intent list below. Don't include additional charater.
Example: {{intent_choices[0]}}
"""


class GraphState(TypedDict):
    messages: list[BaseMessage]
    intent_json_payload: str | None  # Json paylod
    intent_candidate: IntentCandidate | None  # LLM generation
    final_intent: str | None  # Binary decision to run web search


class RagIntentMatcher(IntentMatcher):

    def __init__(
        self,
        agents: list[MessageIntentAgent],
        model_id: str = FIREWORKS_MIXTRAL_22B,
        max_tokens: int = 32768,
    ) -> None:
        super().__init__(
            agents=agents,
        )
        self.llm = ChatFireworks(model=model_id, max_tokens=max_tokens)
        self.match_intent_chain = (
            construct_system_prompt(
                prompt=_MATCH_PROMPT,
                context={
                    "intent_list": self.construct_intent_list,
                    "json_example_payload": EXAMPLE_INTENT_CANDIDATE.perfered_json_serialization,
                },
            )
            | self.llm
        )
        self.refine_intent_chain = (
            construct_system_prompt(
                prompt=_REFLECTION_PROMPT,
                context={"intent_choices": self.intent_keylist},
            )
            | self.llm
        )

        # Build graph
        self.graph = self.build_graph()

    def match_intent_node(self, state: GraphState) -> GraphState:
        logger.debug("match_intent", state=state)
        messages = state["messages"]
        question = messages[0].content
        assert isinstance(question, str), "input question must be text"
        output = self.match_intent_chain.invoke(
            {"messages": [HumanMessage(content=question)]}
        )
        logger.info("match intent output", output=output)
        assert isinstance(output.content, str), "expect output.content to be text"
        intent_candidate = parse_intent_candidate_json(output.content)
        return GraphState(
            messages=messages,
            intent_json_payload=output.content,
            intent_candidate=intent_candidate,
            final_intent=None,
        )

    def refine_intent_node(self, state: GraphState) -> GraphState:
        logger.debug("refine_intent", state=state)
        messages = state["messages"]
        question = messages[0].content
        intent_candidate = state["intent_candidate"]
        intent_json_payload = state["intent_json_payload"]
        assert intent_json_payload, "intent_json_payload must present"
        output = self.refine_intent_chain.invoke(
            {
                "messages": [
                    HumanMessage(content=question),
                    AIMessage(content=intent_json_payload),
                ]
            }
        )
        logger.info("refine intent output", output=output)
        assert isinstance(output.content, str), "expect output.content to be text"
        return GraphState(
            messages=messages,
            intent_json_payload=intent_json_payload,
            intent_candidate=intent_candidate,
            final_intent=output.content,
        )

    def promote_candidate_node(self, state: GraphState) -> GraphState:
        intent_candidate = state["intent_candidate"]
        assert intent_candidate, "intent candidate must not be none."
        return GraphState(
            messages=state["messages"],
            intent_json_payload=state["intent_json_payload"],
            intent_candidate=intent_candidate,
            final_intent=intent_candidate.intent_primary,
        )

    def need_refine_edge(self, state: GraphState) -> str:
        intent_candidate = state["intent_candidate"]
        if intent_candidate and intent_candidate.intent_primary in self.intent_keylist:
            return "NO"
        return "YES"

    def build_graph(self) -> CompiledStateGraph:
        workflow = StateGraph(GraphState)
        # Define the nodes
        workflow.add_node("match_intent", self.match_intent_node)
        workflow.add_node("refine_intent", self.refine_intent_node)
        workflow.add_node("promote_candidate", self.promote_candidate_node)
        # Add edge
        workflow.add_edge(START, "match_intent")
        workflow.add_conditional_edges(
            "match_intent",
            self.need_refine_edge,
            {
                "NO": "promote_candidate",
                "YES": "refine_intent",
            },
        )
        workflow.add_edge("promote_candidate", END)
        workflow.add_edge("refine_intent", END)
        return workflow.compile()

    def parse_intent(self, text: str) -> MessageIntent:
        last_state = self.graph.invoke(
            {
                "messages": [HumanMessage(content=text)],
            },
            {"recursion_limit": 10},
        )
        logger.info("parse intent got last state", last_state=last_state)
        return self.parse_final_state(GraphState(**last_state))

    @cached_property
    def construct_intent_list(self) -> str:
        return "\n---\n".join(
            [
                f"{agent.intent.key}: {agent.description}"
                for _, agent in enumerate(self.agents)
            ]
        )

    @cached_property
    def intent_keylist(self) -> list[str]:
        return [agent.intent.key for _, agent in enumerate(self.agents)]

    def parse_final_state(self, state: GraphState) -> MessageIntent:
        metadata = {
            "method": "rag_matcher",
            "final_intent": state["final_intent"],
        }
        if state["final_intent"]:
            for intent_key in self.intent_keylist:
                if intent_key in state["final_intent"]:
                    return MessageIntent(key=intent_key, metadata=metadata)
        return create_intent(unknown=True)
