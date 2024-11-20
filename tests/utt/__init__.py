import unittest

from fluctlight.utt.template import fstring_format


class TestFStringFormat(unittest.TestCase):
    def test_simple_format(self):
        self.assertEqual(fstring_format("{a} {b}", a=1, b=2), "1 2")

    def test_nested_dict(self):
        self.assertEqual(fstring_format("{a} {b.c}", a=1, b={"c": "hello"}), "1 hello")

    def test_missing_placeholder(self):
        with self.assertRaises(KeyError):
            fstring_format("{a} {b.d}", a=1, b={"c": "hello"})

    def test_deeply_nested_dict(self):
        nested_dict = {"b": {"c": {"d": "deep"}}}
        self.assertEqual(fstring_format("{b.c.d}", **nested_dict), "deep")

    def test_mixed_types(self):
        mixed_types = {"a": 42, "b": {"c": [1, 2, 3]}}
        self.assertEqual(fstring_format("{a} {b.c[1]}", **mixed_types), "42 2")
