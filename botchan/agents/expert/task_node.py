from typing import Any

import structlog
from jinja2 import Template

from botchan.agents.expert.data_mode import TaskConfig
from botchan.constants import GTP_4O_WITH_STRUCT
from botchan.open.chat_utils import simple_assistant, simple_assistant_with_struct_ouput
from botchan.settings import OPENAI_GPT_MODEL_ID
from botchan.task import Task

logger = structlog.getLogger(__name__)


class TaskNode(Task):
    def __init__(self, config: TaskConfig) -> None:
        super().__init__()
        self._config = config
        self.upstream = []

    @property
    def config(self):
        return self._config

    def process(self, *args: Any, **kwds: Any) -> Any:
        inputs = {}
        for key, _type in self.config.input_schema.items():
            inputs[key] = self._require_input(kwargs=kwds, key=key, value_type=_type)

        template = Template(self.config.instruction)
        prompt = template.render(**inputs)

        # output schema is a structure entity
        if self.config.is_structure_output:
            response = simple_assistant_with_struct_ouput(
                model_id=GTP_4O_WITH_STRUCT,
                prompt=prompt,
                output_schema=self.config.output_schema,
            )
        else:
            response = simple_assistant(model_id=OPENAI_GPT_MODEL_ID, prompt=prompt)
        return response
