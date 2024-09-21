from typing import Any

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
        super().__init__(
            intent=intent
        )
        self._name = name
        self._description = description
        self._intent = intent
        self._tasks = self.build_task_graph(task_graph)

    def build_task_graph(self, task_graph: list[TaskConfig]) -> list[TaskNode]:
        return [TaskNode(task_config) for task_config in task_graph]

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
        return message_intent.type == self.intent.type and message_intent.key == self.intent.key


    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def tasks(self) -> list[TaskNode]:
        return self._tasks
