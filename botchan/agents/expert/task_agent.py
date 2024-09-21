from typing import Any, Dict, Set, Tuple

import structlog

from botchan.agents.expert.data_mode import TaskConfig
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
        def build_graph(
            configs: list[TaskConfig],
        ) -> Tuple[TaskNode, Dict[str, TaskNode]]:
            graph_dict: Dict[str, TaskNode] = {}
            root_node: TaskNode | None = None
            for config in configs:
                graph_dict[config.task_key] = TaskNode(config)
            for _, node in graph_dict.items():
                if node.config.is_root:
                    root_node = node
                for upstream_key in node.config.upstream:
                    if upstream_key in graph_dict:
                        upstream_node = graph_dict[upstream_key]
                        node.upstream.append(upstream_node)

            if root_node is None:
                raise ValueError("No root found.")

            return (root_node, graph_dict)

        def topo_sort(
            root: TaskNode, node_graph: Dict[str, TaskNode]
        ) -> list[TaskNode]:
            visited: Set[str] = set()
            temp_marked: Set[str] = set()
            stack: list[TaskNode] = [root]
            visited.add(root.config.task_key)

            def dfs(node: TaskNode):
                if node.config.task_key in temp_marked:
                    raise ValueError("Graph is not a DAG (contains a cycle)")

                if node.config.task_key in visited:
                    return
                temp_marked.add(node.config.task_key)
                for neighbor in node.upstream:
                    dfs(neighbor)
                temp_marked.remove(node.config.task_key)
                visited.add(node.config.task_key)
                stack.append(node)

            for _, node in node_graph.items():
                dfs(node)

            return stack

        root, node_graph = build_graph(task_graph)
        sorted_nodes = topo_sort(root, node_graph)
        logger.info(
            "Task agent build task graph",
            name=self._name,
            all_output=[node.config.task_key for node in sorted_nodes],
        )

        return sorted_nodes

    def process_message(self, message_event: MessageEvent) -> list[str]:
        context = {"message_event": message_event}
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
