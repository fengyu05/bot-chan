import unittest

from fluctlight.agents.expert.data_model import IntakeMessage, TaskConfig, TaskEntity
from fluctlight.agents.expert.task_agent import TaskAgent
from fluctlight.agents.expert.task_node import TaskNode
from fluctlight.intent.message_intent import MessageIntent


class Te1(TaskEntity):
    pass


class TestTaskAgentTopology(unittest.TestCase):
    def setUp(self):
        self.name = "test_agent"
        self.description = "A test agent"
        self.intent = MessageIntent(key="test_task")
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

    def test_build_task_graph_2(self):
        # 1 -> 2 -> 4
        #  \-> 3 -/
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {{message}}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {{step_2}} {{step_3}}",
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
                instruction="User: {{message}}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_5",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {{step_2}} {{step_3}}",
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
                instruction="User: {{message}}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {{step_1}} {{step_3}}",
                input_schema={"step_1": Te1, "step_3": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_5",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {{step_2}}",
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
                instruction="User: {{message}} {{input}}",
                input_schema={"message": IntakeMessage, "input": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {{step_1}}",
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
                instruction="User: {{message}}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {{text}}",
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
        self.assertEqual(str(context.exception)[0:18], "Invalid template o")

    def test_build_task_graph_cycular(self):
        # cycle
        # 1 -> 2 -> 3 -> 4 -> 5
        #  \------>/|         |
        #            \<-------|
        task_graph = [
            TaskConfig(
                task_key="step_1",
                instruction="User: {{message}}",
                input_schema={"message": IntakeMessage},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_2",
                instruction="User: {{step_1}}",
                input_schema={"step_1": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_3",
                instruction="User: {{step_1}} {{step_2}} {{step_5}}",
                input_schema={"step_1": Te1, "step_2": Te1, "step_5": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_4",
                instruction="User: {{step_3}}",
                input_schema={"step_3": Te1},
                output_schema=Te1,
            ),
            TaskConfig(
                task_key="step_5",
                instruction="User: {{step_4}}",
                input_schema={"step_4": Te1},
                output_schema=Te1,
            ),
        ]
        with self.assertRaises(ValueError) as context:
            _ = TaskAgent(self.name, self.description, self.intent, task_graph)
        self.assertEqual(str(context.exception), "Graph contains a cycle.")
