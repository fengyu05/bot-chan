from botchan.agents.expert.data_mode import Task, TaskEntity
from botchan.agents.message_agent import MessageAgent
from botchan.constants import GTP_4O_WITH_STRUCT
from botchan.message_intent import MessageIntent
from botchan.open import OPENAI_CLIENT
from botchan.open.chat_utils import simple_assistant, simple_assistant_with_struct_ouput
from botchan.settings import OPENAI_GPT_MODEL_ID
from botchan.slack.data_model.message_event import MessageEvent

_AGENT_DESC = """A {task_name} task agent handles the request of the following task:
{task_description}
"""


class TaskAgent(MessageAgent):
    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task

    def process_message(self, message_event: MessageEvent) -> list[str]:
        text = message_event.text
        prompt = self.task.instruction.format(text=text)

        if self.task.structure_output:
            response = simple_assistant_with_struct_ouput(
                model_id=GTP_4O_WITH_STRUCT,
                prompt=prompt,
                output_schema=self.task.output_schema,
            )
            return [self.task.metadata, str(response)]
        else:
            response = simple_assistant(model_id=OPENAI_GPT_MODEL_ID, prompt=prompt)
            return [self.task.metadata, response]

    @property
    def description(self):
        return _AGENT_DESC.format(
            task_name=self.task.name, task_description=self.task.description
        )

    @property
    def intent(self):
        return MessageIntent.TASK
