import unittest

from botchan.agents.expert.data_mode import IntakeMessage, TaskConfig, TaskEntity


class Te1(TaskEntity):
    a: str


class Te2(TaskEntity):
    x: int
    tt: Te1


class TestTaskEntityClass(unittest.TestCase):
    def test_check_fields(self):
        self.assertTrue(Te1.check_nested_field_in_class("a"))
        self.assertTrue(Te2.check_nested_field_in_class("x"))
        self.assertTrue(Te2.check_nested_field_in_class("tt.a"))

        self.assertFalse(Te1.check_nested_field_in_class("b"))
        self.assertFalse(Te2.check_nested_field_in_class("y"))
        self.assertFalse(Te2.check_nested_field_in_class("tt.b"))


class TestTaskConfigProperties(unittest.TestCase):
    def test_is_root_property(self):
        config_with_upstream = TaskConfig(
            task_key="task_with_upstream",
            instruction="Test instruction with upstream",
            input_schema={"input_key": Te1},
            output_schema=str,
        )
        self.assertFalse(config_with_upstream.is_root)

        config_without_upstream = TaskConfig(
            task_key="task_without_upstream",
            instruction="Test instruction without upstream",
            input_schema={"message": IntakeMessage},
            output_schema=str,
        )
        self.assertTrue(config_without_upstream.is_root)

    def test_is_structure_output_property(self):
        config_with_structured_output = TaskConfig(
            task_key="task_with_structured_output",
            instruction="Test instruction with structured output",
            input_schema={"input_key": Te1},
            output_schema=Te2,
        )
        self.assertTrue(config_with_structured_output.is_structure_output)

        config_with_unstructured_output = TaskConfig(
            task_key="task_with_unstructured_output",
            instruction="Test instruction with unstructured output",
            input_schema={"input_key": Te1},
            output_schema=str,
        )
        self.assertFalse(config_with_unstructured_output.is_structure_output)


if __name__ == "__main__":
    unittest.main()
