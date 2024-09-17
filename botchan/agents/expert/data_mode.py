from typing import Any, Tuple, Type, Union

from pydantic import BaseModel

from botchan.slack.data_model.message_event import MessageEvent


class TaskEntity(BaseModel):
    def __repr__(self):
        field_strings = [f"{key}: {value}" for key, value in self.dict().items()]
        return "\n".join(field_strings)


class TaskConfig(BaseModel):
    task_key: str
    instruction: str
    input_schema: dict[
        str, Union[Type[MessageEvent], Type[TaskEntity]]
    ]  # map from input name to input type
    output_schema: Union[Type[str], Type[TaskEntity]]
    upstream: list[str] = []

    def __repr__(self) -> str:
        field_strings = [f"{key}: {value}" for key, value in self.dict().items()]
        return "\n".join(field_strings)
    
    @property
    def is_root(self) -> bool:
        """Root node is a node doesn't have upstream dependencies."""
        return len(self.upstream) == 0
    
    @property
    def is_structure_output(self) -> bool:
        return issubclass(self.output_schema, TaskEntity)   