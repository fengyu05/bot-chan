import unittest
from unittest.mock import patch

from botchan.agents.miao_agent import MiaoAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.data_model import MessageEvent
from botchan.intent.message_intent import create_intent
from botchan.intent.openai_intent_matcher import OpenAIIntentMatcher
from tests.data.messages import MESSAGE_EVENT_SIMPLE_1


class TestIntentMatcher(unittest.TestCase):
    def setUp(self):
        self.default_matcher = OpenAIIntentMatcher(
            agents=[
                OpenAiChatAgent(),
                MiaoAgent(),
            ],
            use_strcuture_output=False,
        )

    @patch("botchan.intent.openai_intent_matcher.simple_assistant_with_struct_ouput")
    def test_message_intent_match_llm_with_struct(self, mock_simple_assistant):
        test_intent = create_intent("CHAT")
        mock_simple_assistant.return_value = test_intent

        matcher = OpenAIIntentMatcher(
            agents=[
                OpenAiChatAgent(),
                MiaoAgent(),
            ],
            use_strcuture_output=True,
        )
        message_event_1 = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)
        matcher.match_message_intent(message_event_1)
        mock_simple_assistant.assert_called_once()

    @patch("botchan.intent.openai_intent_matcher.simple_assistant")
    def test_message_intent_match_llm_with_plain_text(self, mock_simple_assistant):
        mock_simple_assistant.return_value = "0"
        matcher = self.default_matcher
        message_event_1 = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)
        matcher.match_message_intent(message_event_1)
        mock_simple_assistant.assert_called_once()
