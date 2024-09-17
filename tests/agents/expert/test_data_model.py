import unittest

from botchan.agents.expert.data_mode import TaskConfig, TaskEntity


class Te1(TaskEntity):
    pass


class Te2(TaskEntity):
    pass


class TestTaskConfigProperties(unittest.TestCase):
    def test_is_root_property(self):
        config_with_upstream = TaskConfig(
            task_key="task_with_upstream",
            instruction="Test instruction with upstream",
            input_schema={"input_key": Te1},
            output_schema=str,
            upstream=["upstream_task_1"],
        )
        self.assertFalse(config_with_upstream.is_root)

        config_without_upstream = TaskConfig(
            task_key="task_without_upstream",
            instruction="Test instruction without upstream",
            input_schema={"input_key": Te2},
            output_schema=str,
            upstream=[],
        )
        self.assertTrue(config_without_upstream.is_root)

    def test_is_structure_output_property(self):
        config_with_structured_output = TaskConfig(
            task_key="task_with_structured_output",
            instruction="Test instruction with structured output",
            input_schema={"input_key": Te1},
            output_schema=Te2,
            upstream=[],
        )
        self.assertTrue(config_with_structured_output.is_structure_output)

        config_with_unstructured_output = TaskConfig(
            task_key="task_with_unstructured_output",
            instruction="Test instruction with unstructured output",
            input_schema={"input_key": Te1},
            output_schema=str,
            upstream=[],
        )
        self.assertFalse(config_with_unstructured_output.is_structure_output)
