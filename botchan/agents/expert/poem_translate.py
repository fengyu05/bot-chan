from botchan.agents.expert.data_mode import Task, TaskEntity
from botchan.agents.expert.task_agent import TaskAgent
from botchan.slack.data_model.message_event import MessageEvent


class PoemTranslation(TaskEntity):
    source_title: str
    source_lang: str
    source_text: str

    target_lang: str
    target_title: str
    target_text: str


def create_poems_translation_task() -> TaskAgent:
    return TaskAgent(
        task=Task(
            name="Poem Translation",
            description="This task translate poem from any source language to tharget lanuage and display them side by side.",
            instruction="Take user input, if input is a peom name, output the information of the poem translate into the user request language. User input: {text}",
            intake=True,
            input_schema=MessageEvent,
            output_schema=PoemTranslation,
            structure_output=True,
        )
    )
