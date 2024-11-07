import unittest
from unittest.mock import patch

from botchan.agents.miao_agent import MiaoAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.intent.intent_agent import IntentAgent
from botchan.intent.intent_matcher_base import IntentMatcher
from botchan.intent.message_intent import UNKNOWN_INTENT, MessageIntent, create_intent
from tests.data.imessages import (
    MESSAGE_HELLO_WORLD,
    MESSAGE_HELLO_WORLD2,
)

_TEST_INTENT = create_intent("test")


class IntentMacherForTest(IntentMatcher):
    def __init__(self, agents: list[IntentAgent]) -> None:
        super().__init__(agents=agents)

    def parse_intent(self, text: str) -> MessageIntent:
        return _TEST_INTENT


class TestMessageIntentAgent(unittest.TestCase):
    def setUp(self):
        self.intent_matcher = IntentMacherForTest(
            agents=[
                OpenAiChatAgent(),
                MiaoAgent(),
            ],
        )

    def test_intent_by_thread(self):
        message1 = MESSAGE_HELLO_WORLD
        message2 = MESSAGE_HELLO_WORLD2

        # Assert the intent cache starts empty
        self.assertNotIn(
            message1.thread_message_id, self.intent_matcher.intent_by_thread
        )
        # Process the first message
        self.intent_matcher.match_message_intent(message1)

        intent_1 = self.intent_matcher.intent_by_thread[message1.thread_message_id]
        self.assertEqual(intent_1, _TEST_INTENT)

        # Process the second message in the same thread
        self.intent_matcher.match_message_intent(message2)

        intent_2 = self.intent_matcher.intent_by_thread[message2.thread_message_id]
        # Assert the two intents should be equal since they are from the same thread
        self.assertEqual(intent_1, intent_2)

    def test_no_text_returns_unknown_intent(self):
        message = MESSAGE_HELLO_WORLD
        message.text = None
        result = self.intent_matcher.match_message_intent(message)

        self.assertEqual(result, UNKNOWN_INTENT)

    @patch("botchan.intent.intent_matcher_base.get_message_intent_by_emoji")
    def test_emoji_based_intent(self, mock_get_message_intent_by_emoji):
        mock_get_message_intent_by_emoji.return_value = create_intent("HAPPY")
        message1 = MESSAGE_HELLO_WORLD

        result = self.intent_matcher.match_message_intent(message1)
        mock_get_message_intent_by_emoji.assert_called_once()
        self.assertEqual(result.key, "HAPPY")


if __name__ == "__main__":
    unittest.main()
