from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Type, Union

from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from typing_extensions import TypedDict

from fluctlight.agents.expert.data_model import TaskEntity

WorkflowSchemaType = Union[TaskEntity, str]


INTERNAL_UPSTREAM_INPUT_MESSAGE = "__INPUT_MESSAGE"
INTERNAL_UPSTREAM_HISTORY_MESSAGES = "__HISTORY_MESSAGES"


class WorkflowNodeLoopMessage(BaseModel):
    mode: Literal["text"]
    message: str


class WorkflowNodeLLMResponse(BaseModel):
    instruction: str


class WorkflowNodeConfig(BaseModel):
    instruction: str
    input_schema: Dict[str, Type[WorkflowSchemaType]]
    output_schema: Type[WorkflowSchemaType]
    loop_message: Optional[WorkflowNodeLoopMessage] = None
    success_criteria: Optional[str] = None  # TODO: move into WorkflowNodeLoopMessage
    llm_response: Optional[WorkflowNodeLLMResponse] = None


class TaskWorkflowConfig(BaseModel):
    nodes: Dict[str, WorkflowNodeConfig]
    begin: str
    end: str


class WorkflowNodeOutput(BaseModel):
    output_type: Literal["SUCCESS", "LOOP_MESSAGE_TRUE", "LOOP_MESSAGE_FALSE"]
    loop_message: Optional[str] = None


class WorkflowRunningState(TypedDict):
    session_id: str
    current_node: str
    running_state: Dict[str, Any]
    output_state: Dict[str, WorkflowNodeOutput]


@dataclass
class WorkflowRunnerConfig:
    config: TaskWorkflowConfig
    state_graph: CompiledStateGraph


def has_internal_upstreams(upstreams: List[str]) -> bool:
    return INTERNAL_UPSTREAM_INPUT_MESSAGE in upstreams


def is_internal_upstream(upstream: str) -> bool:
    if upstream in [
        INTERNAL_UPSTREAM_INPUT_MESSAGE,
        INTERNAL_UPSTREAM_HISTORY_MESSAGES,
    ]:
        return True
    return False
