import unittest
from unittest.mock import MagicMock, patch
from botchan.agents.expert.data_mode import TaskConfig
from botchan.agents.expert.task_agent import TaskAgent
from botchan.agents.expert.task_node import TaskNode
from botchan.slack.data_model import MessageEvent
from botchan.task import Task
from botchan.message_intent import MessageIntent
from tests.data.messages import MESSAGE_EVENT_SIMPLE_1

class TestTaskAgent(unittest.TestCase):

    def setUp(self):
        self.name = "test_agent"
        self.description = "A test agent"
        self.intent = MessageIntent.EXPERT
        self.task_graph = [
            TaskConfig(
                task_key="poem_translation",
                instruction="Take user input, if input is a peom name, output the information of the poem translate into the user request language. User input: {text}",
                input_schema={"message_event": MessageEvent},
                output_schema=str,
            ),
            TaskConfig(
                task_key="peom_grader",
                instruction="Take a poem translation, grade the target translation 3 score of 1-5 integer of 3 crieteria. Rhetroic, Phonetics, Emotion. \n\n Peom: {poem_translation}",
                input_schema={"message_event": MessageEvent},
                output_schema=str,
                upstream=["poem_translation"],
            ),
        ]
        self.message_event = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)


    def test_build_task_graph(self):
        agent = TaskAgent(self.name, self.description, self.intent, self.task_graph)
        self.assertEqual(len(agent.tasks), 2)
        self.assertIsInstance(agent.tasks[0], TaskNode)
        self.assertEqual(agent.tasks[0].config.task_key, "poem_translation")
        self.assertEqual(agent.tasks[1].config.task_key, "peom_grader")

    def test_process_message(self):
        
        task1 = TaskNode(self.task_graph[0])
        task2 = TaskNode(self.task_graph[1])

        # Mock the __call__ method of the tasks
        task1.process = MagicMock(return_value="output_task1")
        task2.process = MagicMock(return_value="output_task2")


        tasks = [task1, task2]
        with patch.object(TaskAgent, 'build_task_graph', return_value=tasks):
            agent = TaskAgent(self.name, self.description, self.intent, self.task_graph)
            
        responses = agent.process_message(message_event=self.message_event) 
        self.assertEqual(responses[1], "output_task1")
        self.assertEqual(responses[3], "output_task2")
        task1.process.assert_called_once_with(message_event=self.message_event)
        task2.process.assert_called_once_with(message_event=self.message_event, poem_translation='output_task1')

