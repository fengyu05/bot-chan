import unittest

from botchan.agents.expert.data_mode import TaskEntity
from botchan.utt.template import fstring_format


class TestFStringFormat(unittest.TestCase):
    def test_simple_format(self):
        self.assertEqual(fstring_format("{a},{b}", a=1, b=2), "1,2")

    def test_nested_dict(self):
        self.assertEqual(fstring_format("{a} {b.c}", a=1, b={"c": "hello"}), "1 hello")

    def test_missing_placeholder(self):
        with self.assertRaises(KeyError):
            fstring_format("{a} {b.d}", a=1, b={"c": "hello"})

    def test_deeply_nested_dict(self):
        nested_dict = {"b": {"c": {"d": "deep"}}}
        self.assertEqual(fstring_format("{b.c.d}", **nested_dict), "deep")

    def test_format_object(self):
        class Te1(TaskEntity):
            value: str

        class Te2(TaskEntity):
            value: int

        self.assertEqual(
            fstring_format(
                "{input1.value}, {input2.value}",
                input1=Te1(value="test"),
                input2=Te2(value=123),
            ),
            "test, 123",
        )
