from dataclasses import dataclass
from typing import Any

import structlog

from fluctlight.agents.message_intent_agent import MessageIntentAgent

logger = structlog.getLogger(__name__)

EMPTY_LOOP_MESSAGE = "Cannot proceed with the request, please try again :bow:"


@dataclass
class TaskInvocationContext:
    context: dict[str, Any]
    current_task_index: int = 0


class WorkflowAgent(MessageIntentAgent):
    pass
