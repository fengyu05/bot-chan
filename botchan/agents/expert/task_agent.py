from dataclasses import dataclass
from typing import Any, Optional

import structlog
from jinja2 import Environment, meta

from botchan.agents.expert.data_model import IntakeMessage, TaskConfig
from botchan.agents.expert.task_node import TaskNode
from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.data_model.slack.message_event import MessageEvent
from botchan.intent.message_intent import MessageIntent

logger = structlog.getLogger(__name__)

EMPTY_LOOP_MESSAGE = "Cannot proceed with the request, please try again :bow:"


@dataclass
class TaskInvocationContext:
    context: dict[str, Any]
    current_task_index: int = 0


class TaskAgent(MessageIntentAgent):
    def __init__(
        self,
        name: str,
        description: str,
        intent: MessageIntent,
        task_graph: list[TaskConfig],
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(intent=intent)
        self._name = name
        self._description = description
        self._intent = intent
        self._context = context or {}
        self._tasks = self.build_task_graph(task_graph)
        self._invocation_contexts = {}

    def build_task_graph(self, task_graph: list[TaskConfig]) -> list[TaskNode]:
        """
        1. check graph
        2. build nodes
        3. toposort
        """

        def topological_sort_util(
            v: str,
            adj: dict[str, TaskNode],
            visited: dict[str, bool],
            rec_stack: dict[str, bool],
            stack: list[TaskNode],
        ):
            if rec_stack[v]:
                raise ValueError("Graph contains a cycle.")

            if visited[v]:
                return True
            rec_stack[v] = True

            # Recur for all adjacent vertices
            for upstream_key, _ in adj[v].config.input_schema.items():
                if upstream_key not in visited:
                    continue
                topological_sort_util(upstream_key, adj, visited, rec_stack, stack)

            # Remove the vertex from recursion stack
            rec_stack[v] = False
            # Mark the current node as visited
            visited[v] = True
            # Push current vertex to stack stores the result
            stack.append(adj[v])

        def topological_sort(adj: dict[str, TaskNode]) -> list[TaskNode]:
            # Stack to store the result
            stack: list[TaskNode] = []

            # Mark all the vertices as not visited
            visited: dict[str, bool] = {key: False for key, _ in adj.items()}
            rec_stack = visited.copy()

            # Call the recursive helper function to store
            # Topological Sort starting from all vertices one by one
            for v, _ in adj.items():
                topological_sort_util(v, adj, visited, rec_stack, stack)

            return stack

        self.check_config(task_graph)
        node_graph: dict[str, TaskNode] = {}
        for config in task_graph:
            node_graph[config.task_key] = TaskNode(config)
        sorted_node = topological_sort(node_graph)
        return sorted_node

    def check_instruction(self, config: TaskConfig) -> None:
        """
        Check whether config.instruction is a valid Jinja2 template that can be filled
        with config.input_schema map.

        Raises:
            ValueError: if the template is invalid or any required variable is missing.
        """
        try:
            env = Environment()
            parsed_content = env.parse(config.instruction)
            # Find undeclared variables in the template
            undeclared_variables = meta.find_undeclared_variables(parsed_content)
            # Check if all required variables are in the input_schema
            missing_vars = undeclared_variables - config.input_schema.keys()
            if missing_vars:
                raise ValueError(
                    f"Missing required variables in input schema: {missing_vars}"
                )
        except Exception as e:
            raise ValueError(
                f"Invalid template or error in template processing: {e}"
            ) from e

    def check_config(self, config_list: list[TaskConfig]):
        has_root = False
        for config in config_list:
            if not has_root and config.is_root:
                has_root = True
            self.check_instruction(config)

        if not has_root:
            raise ValueError(f"No root found. {config_list}")

    def retrieve_context(self, message_event: MessageEvent) -> TaskInvocationContext:
        if message_event.message_id not in self._invocation_contexts:
            self._invocation_contexts[message_event.message_id] = TaskInvocationContext(
                context=self._context.copy()
            )
        return self._invocation_contexts[message_event.message_id]

    def process_message(self, message_event: MessageEvent) -> list[str]:
        ic = self.retrieve_context(message_event)
        assert message_event.text, "message text is missing"
        return self.run_task_with_ic(message_event.text, ic=ic)

    def run_task_with_ic(
        self, message_text: str, ic: TaskInvocationContext
    ) -> list[str]:
        ic.context.update({"message": IntakeMessage(text=message_text)})
        responses = []

        for index, task in enumerate(self._tasks):
            if index != ic.current_task_index:
                continue

            output = task(**ic.context)
            ic.context[task.config.task_key] = output

            responses.append(str(task.config))
            responses.append(str(output))
            if self.stuck_in_loop(task=task, output=output):
                responses.append(task.config.loop_message or EMPTY_LOOP_MESSAGE)
                break

            # Task success update ic status
            ic.current_task_index += 1

        logger.info(
            "Task agent process message", name=self._name, all_output=ic.context
        )
        return responses

    def stuck_in_loop(self, task: TaskNode, output: Any) -> bool:
        if task.config.success_criteria is None:
            return False

        return not task.config.success_criteria(output)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def tasks(self) -> list[TaskNode]:
        return self._tasks
