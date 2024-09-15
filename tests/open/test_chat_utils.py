import unittest
from unittest.mock import MagicMock


def get_message_from_response(response, idx: int = 0) -> str:
    return response.choices[idx].message.content


class TestGetMessageFromResponse(unittest.TestCase):
    def setUp(self):
        # Setup mock responses for testing
        self.response_single = MagicMock()
        self.response_multiple = MagicMock()

        # Mock single choice response
        self.response_single.choices = [
            MagicMock(message=MagicMock(content="Hello World"))
        ]

        # Mock multiple choice response
        self.response_multiple.choices = [
            MagicMock(message=MagicMock(content="First Message")),
            MagicMock(message=MagicMock(content="Second Message")),
        ]

    def test_single_choice(self):
        self.assertEqual(get_message_from_response(self.response_single), "Hello World")

    def test_multiple_choices_first(self):
        self.assertEqual(
            get_message_from_response(self.response_multiple, idx=0), "First Message"
        )

    def test_multiple_choices_second(self):
        self.assertEqual(
            get_message_from_response(self.response_multiple, idx=1), "Second Message"
        )

    def test_index_out_of_range(self):
        with self.assertRaises(IndexError):
            get_message_from_response(self.response_single, idx=1)
