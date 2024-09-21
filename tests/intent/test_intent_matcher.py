import unittest
from unittest.mock import patch

from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.agents.miao_agent import MiaoAgent
from botchan.intent.message_intent import create_intent
from botchan.intent.intent_matcher import IntentMatcher
from botchan.slack.data_model import MessageEvent
from tests.data.messages import MESSAGE_EVENT_REPLY_TO_SIMPLE_1, MESSAGE_EVENT_SIMPLE_1


class TestIntentMatcher(unittest.TestCase):
    def setUp(self):
        self.default_matcher = IntentMatcher(
            agents=[
                OpenAiChatAgent(),
                MiaoAgent(),
            ],
            use_llm=True,
            use_strcuture_output=False,
        )

    @patch('botchan.intent.intent_matcher.simple_assistant_with_struct_ouput')
    def test_message_intent_match_llm_with_struct(self, mock_simple_assistant):
        test_intent = create_intent('CHAT')
        mock_simple_assistant.return_value = test_intent

        matcher = IntentMatcher(
            agents=[
                OpenAiChatAgent(),
                MiaoAgent(),
            ],
            use_llm=True,
            use_strcuture_output=True,
        )
        message_event_1 = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)
        message_event_2 = MessageEvent(**MESSAGE_EVENT_REPLY_TO_SIMPLE_1)

        # Assert the intent cache starts empty
        self.assertNotIn(message_event_1.thread_message_id, matcher.intent_by_thread)
        # Process the first message
        matcher.match_message_intent(message_event_1)

        intent_1 = matcher.intent_by_thread[message_event_1.thread_message_id]
        self.assertEqual(intent_1, test_intent)

        # Process the second message in the same thread
        matcher.match_message_intent(message_event_2)

        intent_2 = matcher.intent_by_thread[message_event_2.thread_message_id]
        # Assert the two intents should be equal since they are from the same thread
        self.assertEqual(intent_1, intent_2)

        mock_simple_assistant.asert_called_once()  # Call only once, second time is in cache


    @patch('botchan.intent.intent_matcher.simple_assistant')
    def test_message_intent_match_llm_with_plain_text(self, mock_simple_assistant):
        test_intent = create_intent('CHAT')
        mock_simple_assistant.return_value = '0'
        matcher = self.default_matcher
        message_event_1 = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)
        # Assert the intent cache starts empty
        self.assertNotIn(message_event_1.thread_message_id, matcher.intent_by_thread)
        # Process the first message
        matcher.match_message_intent(message_event_1)
        intent_1 = matcher.intent_by_thread[message_event_1.thread_message_id]
        self.assertEqual(intent_1, test_intent)
        mock_simple_assistant.asert_called_once()  # Call only once, second time is in cache
