import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.message_intent import MessageIntent
from botchan.multi_intent_agent import MessageMultiIntentAgent
from botchan.slack.data_model import MessageCreateEvent
from tests.data.messages import MESSAGE_EVENT_REPLY_TO_SIMPLE_1, MESSAGE_EVENT_SIMPLE_1


class TestMessageMultiIntentAgent(unittest.TestCase):
    # All these mock is mocking the method import by multi_intent_agent directly
    @patch("botchan.multi_intent_agent.slack_auth.get_bot_user_id")
    @patch("botchan.multi_intent_agent.slack_reaction.add_reaction")
    @patch("botchan.multi_intent_agent.slack_chat.reply_to_message")
    @patch("botchan.multi_intent_agent.simple_assistant")
    def test_message_intent_consistency(
        self, mock_simple_assistant, mock_reply, mock_add_reaction, mock_get_bot_user_id
    ):
        # Mock Bot User ID
        mock_get_bot_user_id.return_value = "B12345678"

        # Mock simple_assistant
        mock_simple_assistant.return_value = "CHAT"

        with patch.object(
            OpenAiChatAgent, "process_message", return_value=["Hello"]
        ) as mock_process_message:
            # Create an instance of the agent with a mocked slack client
            slack_client_mock = MagicMock()
            agent = MessageMultiIntentAgent(slack_client=slack_client_mock)

            # Mocked message event
            message_event_1 = MessageCreateEvent(**MESSAGE_EVENT_SIMPLE_1)
            message_event_2 = MessageCreateEvent(**MESSAGE_EVENT_REPLY_TO_SIMPLE_1)

            # Assert the intent cache starts empty
            self.assertNotIn(message_event_1.thread_message_id, agent.intent_by_thread)
            # Process the first message
            agent.receive_message(message_event_1)
            intent_1 = agent.intent_by_thread[message_event_1.thread_message_id]
            self.assertEqual(intent_1, MessageIntent.CHAT)

            # Process the second message in the same thread
            agent.receive_message(message_event_2)

            intent_2 = agent.intent_by_thread[message_event_2.thread_message_id]

            # Assert the two intents should be equal since they are from the same thread
            self.assertEqual(intent_1, intent_2)

            mock_simple_assistant.asert_called_once()  # Call only once, second time is in cache
            mock_add_reaction.assert_called()
            mock_reply.assert_called()
            mock_process_message.assert_called()
