from typing import Type, Union

from pydantic import BaseModel

from botchan.slack.data_model.message_event import MessageEvent


class TaskEntity(BaseModel):
    def __repr__(self):
        field_strings = [f"{key}: {value}" for key, value in self.dict().items()]
        return "\n".join(field_strings)


class Task(BaseModel):
    name: str
    description: str
    instruction: str
    intake: bool  # Whether this task take raw message as input
    input_schema: Union[Type[MessageEvent], Type[TaskEntity]]
    output_schema: Type[TaskEntity]
    structure_output: bool  # Whether this task output structure entity

    @property
    def metadata(self) -> str:
        return f"Expert Task: {self.name}, intake: {self.intake}, strcuture: {self.structure_output}, input_schema: {self.input_schema.__name__}, output_schema: {self.output_schema.__name__}"
