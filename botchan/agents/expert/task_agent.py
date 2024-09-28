from typing import Any

import structlog

from botchan.agents.expert.data_mode import IntakeMessage, TaskConfig
from botchan.agents.expert.task_node import TaskNode
from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.intent.message_intent import MessageIntent, MessageIntentType
from botchan.slack.data_model.message_event import MessageEvent

logger = structlog.getLogger(__name__)


class TaskAgent(MessageIntentAgent):
    def __init__(
        self,
        name: str,
        description: str,
        intent: MessageIntent,
        task_graph: list[TaskConfig],
    ) -> None:
        super().__init__(intent=intent)
        self._name = name
        self._description = description
        self._intent = intent
        self._tasks = self.build_task_graph(task_graph)

    def build_task_graph(self, task_graph: list[TaskConfig]) -> list[TaskNode]:
        """
        1. build graph from input_schema, set up Task upstreams, downstream pointers.
        2. check whether it's valid(raise execption)
            1. Root tasks must take consume message only.
            2. instruction only has fields in the input object.
            3 .no pending inputs
        3. topo sort accordingly
        """

        def check_instruction(config: TaskConfig):
            # TODO:
            for key, _ in config.input_schema.items():
                if config.instruction.find("{" + key) < 0:
                    raise ValueError("Instruction fields not match input object.")

        def check_config(config_list: list[TaskConfig]):
            has_root = False
            for config in config_list:
                # check has root
                if not has_root and config.is_root:
                    has_root = True
                # check instruction
                check_instruction(config)

            if not has_root:
                raise ValueError(f"No root found. {config_list}")

        def build_graph(config_list: list[TaskConfig]) -> dict[str, TaskNode]:
            graph_dict: dict[str, TaskNode] = {}
            for config in config_list:
                graph_dict[config.task_key] = TaskNode(config)
            return graph_dict

        def topological_sort_util(
            v: str,
            adj: dict[str, TaskNode],
            visited: dict[str, bool],
            stack: list[TaskNode],
        ):
            # Mark the current node as visited
            visited[v] = True

            # Recur for all adjacent vertices
            for upstream_key, _ in adj[v].config.input_schema.items():
                if upstream_key not in visited:
                    continue
                if not visited[upstream_key]:
                    topological_sort_util(upstream_key, adj, visited, stack)

            # Push current vertex to stack stores the result
            stack.append(adj[v])

        def topological_sort(adj: dict[str, TaskNode]) -> list[TaskNode]:
            # Stack to store the result
            stack: list[TaskNode] = []

            visited: dict[str, bool] = {key: False for key, _ in adj.items()}

            for v, _ in adj.items():
                if not visited[v]:
                    topological_sort_util(v, adj, visited, stack)

            return stack

        check_config(task_graph)
        node_graph = build_graph(task_graph)
        sorted_node = topological_sort(node_graph)
        logger.info(
            "Build task graph finish",
            name=self._name,
            all_output=[n.config.task_key for n in sorted_node],
        )
        return sorted_node

    def process_message(self, message_event: MessageEvent) -> list[str]:
        context = {"message": IntakeMessage(text=message_event.text)}
        responses = []
        for task in self._tasks:
            responses.append(str(task.config))
            output = task(**context)
            responses.append(str(output))
            context[task.config.task_key] = output
        logger.info("Task agent process message", name=self._name, all_output=context)
        return responses

    def should_process(
        self, *args: Any, **kwds: Any
    ) -> bool:  # pylint: disable=unused-argument
        message_intent: MessageIntent = self._require_input(
            kwargs=kwds, key="message_intent"
        )
        return (
            message_intent.type == self.intent.type
            and message_intent.key == self.intent.key
        )

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def tasks(self) -> list[TaskNode]:
        return self._tasks
