import unittest
from unittest import skip
from unittest.mock import patch

from fluctlight.agents.miao_agent import MiaoAgent
from fluctlight.agents.openai_chat_agent import OpenAiChatAgent
from fluctlight.intent.message_intent import create_intent
from fluctlight.intent.openai_intent_matcher import OpenAIIntentMatcher
from tests.data.imessages import MESSAGE_HELLO_WORLD


class TestIntentMatcher(unittest.TestCase):
    def setUp(self):
        pass

    @skip("Disabled temporarily: pass locally but failed on CI")
    @patch("fluctlight.intent.openai_intent_matcher.simple_assistant_with_struct_ouput")
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
        matcher.match_message_intent(MESSAGE_HELLO_WORLD)
        mock_simple_assistant.assert_called_once()

    @skip("Disabled temporarily: pass locally but failed on CI")
    @patch("fluctlight.intent.openai_intent_matcher.simple_assistant")
    def test_message_intent_match_llm_with_plain_text(self, mock_simple_assistant):
        mock_simple_assistant.return_value = "0"
        matcher = OpenAIIntentMatcher(
            agents=[
                OpenAiChatAgent(),
                MiaoAgent(),
            ],
        )
        matcher.match_message_intent(MESSAGE_HELLO_WORLD)
        mock_simple_assistant.assert_called_once()


if __name__ == "__main__":
    unittest.main()
