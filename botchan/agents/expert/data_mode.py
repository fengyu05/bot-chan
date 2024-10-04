from typing import Callable, Type, Union, Optional

from pydantic import BaseModel


class TaskEntity(BaseModel):
    def __repr__(self):
        field_strings = [f"{key}: {value}" for key, value in self.dict().items()]
        return "\n".join(field_strings)


class IntakeMessage(TaskEntity):
    text: str


class TaskConfig(BaseModel):
    task_key: str
    instruction: str
    input_schema: dict[str, Type[TaskEntity]]  # map from input name to input type
    output_schema: Union[Type[str], Type[TaskEntity]]
    success_criteria: Optional[Callable]
    loop_message: Optional[str]

    def __repr__(self) -> str:
        field_strings = [f"{key}: {value}" for key, value in self.dict().items()]
        return "\n".join(field_strings)

    @property
    def is_root(self) -> bool:
        """Root node is node only has intake Message"""
        return [IntakeMessage] == list(self.input_schema.values())

    @property
    def is_structure_output(self) -> bool:
        return issubclass(self.output_schema, TaskEntity)
