from typing import Any, Callable, Dict, Hashable, List, Type, cast

from jinja2 import Template

# from langchain_fireworks import ChatFireworks
# from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langsmith import traceable
from openai.types.chat import ChatCompletion, ParsedChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel

from fluctlight.agents.expert.data_model import TaskEntity
from fluctlight.agents.expert.task_workflow_config import (
    INTERNAL_UPSTREAM_HISTORY_MESSAGES,
    INTERNAL_UPSTREAM_INPUT_MESSAGE,
    TaskWorkflowConfig,
    WorkflowNodeConfig,
    WorkflowNodeOutput,
    WorkflowRunningState,
    is_internal_upstream,
)
from fluctlight.open import OPENAI_CLIENT


@traceable(run_type="llm")
def chat_completion(
    output_schema: Type[Any], messages: List[ChatCompletionMessageParam]
) -> ParsedChatCompletion:
    model = "gpt-4o-mini-2024-07-18"
    # model="gpt-4o-2024-08-06"
    completion = OPENAI_CLIENT.beta.chat.completions.parse(
        temperature=0,
        model=model,
        messages=messages,
        response_format=output_schema,
    )
    return completion


def create_workflow_node(
    name: str,
    config: WorkflowNodeConfig,
) -> Callable[[WorkflowRunningState], WorkflowRunningState]:
    def workflow_fn(state: WorkflowRunningState) -> WorkflowRunningState:
        running_state = state["running_state"]

        # LLM instruction
        template = Template(config.instruction)
        text = template.render(running_state)

        messages = [
            {
                "role": "system",
                "content": text,
            },
        ]

        # LLM structured output
        response = chat_completion(config.output_schema, messages)
        structured_content = response.choices[0].message.parsed

        new_state = state.copy()
        new_state["running_state"] = new_state["running_state"].copy()
        new_state["output_state"] = new_state["output_state"].copy()

        # Check output state
        if structured_content and isinstance(structured_content, config.output_schema):
            if isinstance(structured_content, TaskEntity) or isinstance(
                structured_content, str
            ):
                new_state["running_state"][name] = structured_content
                new_state["output_state"][name] = WorkflowNodeOutput(
                    output_type="SUCCESS"
                )
            else:
                raise ValueError(f"Output type not match, {structured_content}")

        return new_state

    return workflow_fn


def create_workflow_loop_output_node(
    name: str,
    config: WorkflowNodeConfig,
    success: bool,
) -> Callable[[WorkflowRunningState], WorkflowRunningState]:
    mode = "text"
    if config.loop_message:
        mode = config.loop_message.mode
        loop_message = config.loop_message.message
    else:
        loop_message = ""

    def loop_output_fn(state: WorkflowRunningState) -> WorkflowRunningState:
        running_state = state["running_state"]
        template = Template(loop_message)
        text = template.render(running_state)

        if mode == "text":
            pass
        elif mode == "llm":
            # TODO: text is llm instruction
            pass

        new_state = state.copy()
        # new_state["running_state"] = new_state["running_state"].copy()
        new_state["output_state"] = new_state["output_state"].copy()

        if success:
            new_state["output_state"][name] = WorkflowNodeOutput(
                output_type="LOOP_MESSAGE_TRUE",
            )
        else:
            new_state["output_state"][name] = WorkflowNodeOutput(
                output_type="LOOP_MESSAGE_FALSE",
                loop_message=text,
            )

        return new_state

    return loop_output_fn


def workflow_node_router(state: WorkflowRunningState) -> str:
    cur_node = state["current_node"]

    if cur_node == "":
        raise ValueError(f"Workflow running state no node found. {state}")
    return cur_node


class ConditionalOutput(BaseModel):
    is_match_success_criteria: bool


def create_conditional_edge_chain(
    name: str,
    node_config: WorkflowNodeConfig,
) -> Callable[[WorkflowRunningState], str]:
    success_criteria: str = node_config.success_criteria or ""

    def node_conditional_edge(state: WorkflowRunningState) -> str:
        context = state["running_state"]

        template = Template(success_criteria)
        text = template.render(context)

        messages = [
            {
                "role": "system",
                "content": text,
            },
        ]

        result = "NO"

        response = chat_completion(ConditionalOutput, messages)
        structured_content = response.choices[0].message.parsed
        if isinstance(structured_content, ConditionalOutput):
            if cast(ConditionalOutput, structured_content).is_match_success_criteria:
                result = "YES"

        return result

    return node_conditional_edge


# START -> router -> nodes... -> END
def build_workflow_graph(config: TaskWorkflowConfig) -> CompiledStateGraph:
    workflow = StateGraph(WorkflowRunningState)

    workflow_node_route_table: Dict[Hashable, str] = {}

    # Build and add nodes
    for k, v in config.nodes.items():
        # add node route
        workflow_node_route_table[k] = k

        # add nodes
        workflow.add_node(k, create_workflow_node(k, v))

    # Add START -> node router
    workflow.add_conditional_edges(
        START, workflow_node_router, workflow_node_route_table
    )

    # Add edges
    for k, v in config.nodes.items():
        if v.success_criteria:
            # Add loop output node
            workflow.add_node(
                k + "_LOOP_OUTPUT_TRUE",
                create_workflow_loop_output_node(k, v, True),
            )
            workflow.add_node(
                k + "_LOOP_OUTPUT_FALSE",
                create_workflow_loop_output_node(k, v, False),
            )
            # Add loop node edges
            workflow.add_edge(k + "_LOOP_OUTPUT_TRUE", END)
            workflow.add_edge(k + "_LOOP_OUTPUT_FALSE", END)
            workflow.add_conditional_edges(
                k,
                create_conditional_edge_chain(k, v),
                {
                    "YES": k + "_LOOP_OUTPUT_TRUE",
                    "NO": k + "_LOOP_OUTPUT_FALSE",
                },
            )
        else:
            # normal node end edge
            workflow.add_edge(k, END)

    graph = workflow.compile()

    # show_graph_mermaid(config, graph)

    return graph


def show_graph_mermaid(config: TaskWorkflowConfig, graph: CompiledStateGraph):
    from io import BytesIO

    import matplotlib.pyplot as plt
    from PIL import Image

    # logical graph
    def fn(state):
        return state

    def edge_fn(state) -> str:
        return ""

    wf = StateGraph(WorkflowRunningState)
    for k, v in config.nodes.items():
        wf.add_node(k, fn)
    for n in ["INPUT_MESSAGE", "HISTORY_MESSAGES"]:
        wf.add_node(n, fn)
        wf.add_edge(START, n)
    wf.add_edge(START, config.begin)
    wf.add_edge(config.end, END)
    for k, v in config.nodes.items():
        for upstream, _ in v.input_schema.items():
            if is_internal_upstream(upstream):
                if upstream == INTERNAL_UPSTREAM_INPUT_MESSAGE:
                    wf.add_edge("INPUT_MESSAGE", k)
                elif upstream == INTERNAL_UPSTREAM_HISTORY_MESSAGES:
                    wf.add_edge("HISTORY_MESSAGES", k)
                continue
            if config.nodes[upstream].success_criteria:
                wf.add_conditional_edges(
                    upstream, edge_fn, {"YES": k, "NO: Loop Message": upstream}
                )
            else:
                wf.add_edge(upstream, k)

    logical_graph = wf.compile()
    image1 = Image.open(BytesIO(logical_graph.get_graph().draw_mermaid_png()))

    # executable graph
    graph_bytes = graph.get_graph().draw_mermaid_png()
    image2 = Image.open(BytesIO(graph_bytes))

    total_height = image1.height + image2.height
    max_width = max(image1.width, image2.width)

    combined_image = Image.new("RGB", (max_width, total_height), (255, 255, 255))
    combined_image.paste(image1, ((max_width - image1.width) // 2, 0))
    combined_image.paste(image2, ((max_width - image2.width) // 2, image1.height))

    plt.imshow(combined_image)

    plt.axis("off")
    plt.title("Graph Visualization from PNG Bytes")
    plt.show()
