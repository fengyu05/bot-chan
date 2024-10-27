import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.expert.poem_translate import INTENT_KEY as poem_translate_intent_key
from botchan.agents.expert.poem_translate import create_poems_translation_task_agent
from botchan.agents.expert.shopping_assisist import (
    INTENT_KEY as shopping_assisist_intent_key,
)
from botchan.agents.expert.shopping_assisist import create_shopping_assisist_task_agent
from botchan.agents.miao_agent import MiaoAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.intent.message_intent import create_intent
from botchan.intent.rag_intent_matcher import (
    RagIntentMatcher,  # Replace with the actual module name
)
from tests.intergation_test_utils import skip_integration_tests


class TestRagIntentMatcher(unittest.TestCase):

    def setUp(self) -> None:

        self.agents = [
            OpenAiChatAgent(),  ## Handle simple chat
            MiaoAgent(),
            create_poems_translation_task_agent(),
            create_shopping_assisist_task_agent(),
        ]
        return super().setUp()

    @skip_integration_tests
    def test_parse_intent_miao(self):
        rag_intent_matcher = RagIntentMatcher(self.agents)
        result = rag_intent_matcher.parse_intent("Let's talk in miao tune")
        self.assertTrue(result.equal_wo_metadata(create_intent("miao")))

    @skip_integration_tests
    def test_parse_intent_chat(self):
        rag_intent_matcher = RagIntentMatcher(self.agents)
        result = rag_intent_matcher.parse_intent("Let's have a free chat")
        self.assertTrue(result.equal_wo_metadata(create_intent("chat")))

    # Fix the _ escape issue with reflection
    # @skip_integration_tests
    # def test_parse_intent_poem_translate(self):
    #     rag_intent_matcher = RagIntentMatcher(self.agents)
    #     result = rag_intent_matcher.parse_intent("静夜思 English")
    #     self.assertTrue(
    #         result.equal_wo_metadata(create_intent(poem_translate_intent_key))
    #     )

    @skip_integration_tests
    def test_parse_intent_shopping(self):
        rag_intent_matcher = RagIntentMatcher(self.agents)
        result = rag_intent_matcher.parse_intent("Help me order sth")
        self.assertTrue(
            result.equal_wo_metadata(create_intent(shopping_assisist_intent_key))
        )


# Run the tests
if __name__ == "__main__":
    unittest.main()
