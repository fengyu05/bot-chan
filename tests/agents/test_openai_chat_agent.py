import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.openai_chat_agent import OpenAiChatAgent
from tests.data.imessages import MESSAGE_HELLO_WORLD, MESSAGE_HELLO_WORLD2


class TestOpenAiChatAgent(unittest.TestCase):
    @patch("botchan.agents.openai_chat_agent.OPENAI_CLIENT.chat.completions.create")
    def test_process_message_plain_text(self, mock_create):
        # Mocking OpenAI response
        mock_response_text = "mocked response from OpenAI"
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=mock_response_text))
        ]
        mock_create.return_value = mock_response

        agent = OpenAiChatAgent(get_message_by_event=None)

        response1 = agent.process_message(MESSAGE_HELLO_WORLD)
        response2 = agent.process_message(MESSAGE_HELLO_WORLD2)

        self.assertEqual(response1, [mock_response_text])
        self.assertEqual(response2, [mock_response_text])
        self.assertEqual(mock_create.call_count, 2)

        self.assertEqual(
            5, len(agent.message_buffer[MESSAGE_HELLO_WORLD.thread_message_id])
        )
        # Optionally, assert the types or contents of these messages, if needed:
        expected_order = ["system", "user", "assistant", "user", "assistant"]
        for i, message in enumerate(
            agent.message_buffer[MESSAGE_HELLO_WORLD.thread_message_id]
        ):
            # Replace 'type' with the actual key used to determine message type
            self.assertEqual(expected_order[i], message["role"])

    @patch("botchan.agents.openai_chat_agent.OPENAI_CLIENT.chat.completions.create")
    def test_process_message_plain_text_same_thread(self, mock_create):
        # Mocking OpenAI response
        mock_response_text = "mocked response from OpenAI"
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=mock_response_text))
        ]
        mock_create.return_value = mock_response

        agent = OpenAiChatAgent(get_message_by_event=None)

        response = agent.process_message(MESSAGE_HELLO_WORLD)

        self.assertEqual(response, [mock_response_text])
        self.assertIn(MESSAGE_HELLO_WORLD.thread_message_id, agent.message_buffer)
        mock_create.assert_called_once()

    # @patch("botchan.agents.openai_chat_agent.OPENAI_CLIENT.chat.completions.create")
    # @patch("botchan.agents.openai_chat_agent.SLACK_TRANSCRIBE_WAIT_SEC", 0)
    # def test_process_message_with_files(self, mock_create):
    #     event = MESSAGE_AUDIO_EVENT_1
    #     # Mocking OpenAI response
    #     mock_response_text = "mocked response from OpenAI"
    #     mock_response = MagicMock()
    #     mock_response.choices = [
    #         MagicMock(message=MagicMock(content=mock_response_text))
    #     ]
    #     mock_create.return_value = mock_response

    #     # Mocking Slack fetch message response
    #     mock_file_object = MagicMock()
    #     mock_file_object.get_transcription_preview.return_value = "transcribed text"

    #     get_message_by_event_mock = MagicMock(
    #         return_value=MessageEvent(**MESSAGE_AUDIO_EVENT_2)
    #     )

    #     agent = OpenAiChatAgent(
    #         get_message_by_event=get_message_by_event_mock, buffer_limit=2
    #     )

    #     response = agent.process_message(MessageEvent(**event))

    #     self.assertEqual(response, [mock_response_text])
    #     self.assertIn(f"{event['channel']}|{event['event_ts']}", agent.message_buffer)
    #     mock_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
