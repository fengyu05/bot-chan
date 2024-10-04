import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.expert.data_mode import IntakeMessage, TaskConfig, TaskEntity
from botchan.agents.expert.task_agent import TaskAgent
from botchan.agents.expert.task_node import TaskNode
from botchan.intent.message_intent import MessageIntent, MessageIntentType
from botchan.slack.data_model import MessageEvent
from tests.data.messages import MESSAGE_EVENT_SIMPLE_1


class Te1(TaskEntity):
    pass


class TestTaskAgent(unittest.TestCase):
    def setUp(self):
        self.name = "test_agent"
        self.description = "A test agent"
        self.intent = MessageIntent(type=MessageIntentType.EXPERT, key="test_task")
        self.task_graph = [
            TaskConfig(
                task_key="poem_translation",
                instruction="Take user input, if input is a peom name, output the information of the poem translate into the user request language. User input: {message}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="peom_grader",
                instruction="Take a poem translation, grade the target translation 3 score of 1-5 integer of 3 crieteria. Rhetroic, Phonetics, Emotion. \n\n Peom: {poem_translation}",
                input_schema={"poem_translation": IntakeMessage},
                output_schema=str,
            ),
        ]
        self.message_event = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)
        self.intake_message = IntakeMessage(text=self.message_event.text)

    def test_process_message(self):
        task1 = TaskNode(self.task_graph[0])
        task2 = TaskNode(self.task_graph[1])

        # Mock the __call__ method of the tasks
        task1.process = MagicMock(return_value="output_task1")
        task2.process = MagicMock(return_value="output_task2")

        tasks = [task1, task2]
        with patch.object(TaskAgent, "build_task_graph", return_value=tasks):
            agent = TaskAgent(
                name=self.name,
                description=self.description,
                intent=self.intent,
                task_graph=self.task_graph,
            )

        responses = agent.process_message(message_event=self.message_event)
        self.assertEqual(responses[1], "output_task1")
        self.assertEqual(responses[3], "output_task2")
        task1.process.assert_called_once_with(message=self.intake_message)
        task2.process.assert_called_once_with(
            message=self.intake_message, poem_translation="output_task1"
        )

    def test_process_message_with_context(self):
        task1 = TaskNode(self.task_graph[0])
        task2 = TaskNode(self.task_graph[1])

        # Mock the __call__ method of the tasks
        task1.process = MagicMock(return_value="output_task1")
        task2.process = MagicMock(return_value="output_task2")

        tasks = [task1, task2]
        with patch.object(TaskAgent, "build_task_graph", return_value=tasks):
            agent = TaskAgent(
                name=self.name,
                description=self.description,
                intent=self.intent,
                task_graph=self.task_graph,
                context={
                    "a": "a",
                    "b": 1,
                },
            )

        agent.process_message(message_event=self.message_event)
        task1.process.assert_called_once_with(
            message=self.intake_message,
            a="a",
            b=1,
        )
        task2.process.assert_called_once_with(
            message=self.intake_message,
            poem_translation="output_task1",
            a="a",
            b=1,
        )

    def test_build_task_graph_2(self):
        # 1 -> 2 -> 4
        #  \-> 3 -/
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {message}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {step_2} {step_3}",
                input_schema={"step_2": Te1, "step_3": Te1},
                output_schema=Te1,
            ),
        ]
        agent = TaskAgent(
            name=self.name,
            description=self.description,
            intent=self.intent,
            task_graph=task_graph,
        )
        self.assertEqual(len(agent.tasks), 4)
        self.assertIsInstance(agent.tasks[0], TaskNode)
        self.assertEqual(agent.tasks[0].config.task_key, "step_1")
        self.assertEqual(agent.tasks[1].config.task_key, "step_2")
        self.assertEqual(agent.tasks[2].config.task_key, "step_3")
        self.assertEqual(agent.tasks[3].config.task_key, "step_4")

    def test_build_task_graph_3(self):
        #  /-> 5
        # 1 -> 2 -> 4
        #  \-> 3 -/
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {message}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_5",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {step_2} {step_3}",
                input_schema={"step_2": Te1, "step_3": Te1},
                output_schema=Te1,
            ),
        ]
        agent = TaskAgent(
            name=self.name,
            description=self.description,
            intent=self.intent,
            task_graph=task_graph,
        )
        self.assertEqual(len(agent.tasks), 5)
        self.assertIsInstance(agent.tasks[0], TaskNode)
        self.assertEqual(agent.tasks[0].config.task_key, "step_1")
        self.assertEqual(agent.tasks[1].config.task_key, "step_5")
        self.assertEqual(agent.tasks[2].config.task_key, "step_2")
        self.assertEqual(agent.tasks[3].config.task_key, "step_3")
        self.assertEqual(agent.tasks[4].config.task_key, "step_4")

    def test_build_task_graph_4(self):
        # 1 -> 2 -> 3 -> 4
        #  \--------->/
        #   \-> 5
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {message}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {step_1} {step_3}",
                input_schema={"step_1": Te1, "step_3": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_5",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {step_2}",
                input_schema={"step_2": Te1},
                output_schema=Te1,
            ),
        ]
        agent = TaskAgent(
            name=self.name,
            description=self.description,
            intent=self.intent,
            task_graph=task_graph,
        )
        self.assertEqual(len(agent.tasks), 5)
        self.assertIsInstance(agent.tasks[0], TaskNode)
        self.assertEqual(agent.tasks[0].config.task_key, "step_1")
        self.assertEqual(agent.tasks[1].config.task_key, "step_2")
        self.assertEqual(agent.tasks[2].config.task_key, "step_3")
        self.assertEqual(agent.tasks[3].config.task_key, "step_4")
        self.assertEqual(agent.tasks[4].config.task_key, "step_5")

    def test_build_task_graph_no_root_exception(self):
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {message} {input}",
                input_schema={"message": IntakeMessage, "input": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
        ]
        with self.assertRaises(ValueError) as context:
            _ = TaskAgent(
                name=self.name,
                description=self.description,
                intent=self.intent,
                task_graph=task_graph,
            )
        self.assertEqual(str(context.exception)[0:14], "No root found.")

    def test_build_task_graph_instruction_fields_not_match(self):
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {message}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {text}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
        ]
        with self.assertRaises(ValueError) as context:
            _ = TaskAgent(
                name=self.name,
                description=self.description,
                intent=self.intent,
                task_graph=task_graph,
            )
        self.assertEqual(str(context.exception)[0:18], "Instruction fields")

    def test_build_task_graph_cycular(self):
        # cycle
        # 1 -> 2 -> 3 -> 4 -> 5
        #  \------>/|         |
        #            \<-------|
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {message}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {step_1}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {step_1} {step_2} {step_5}",
                input_schema={"step_1": Te1, "step_2": Te1, "step_5": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {step_3}",
                input_schema={"step_3": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_5",
                instruction="User: {step_4}",
                input_schema={"step_4": Te1},
                output_schema=Te1,
            ),
        ]
        with self.assertRaises(ValueError) as context:
            _ = TaskAgent(self.name, self.description, self.intent, task_graph)
        self.assertEqual(str(context.exception), "Graph contains a cycle.")
