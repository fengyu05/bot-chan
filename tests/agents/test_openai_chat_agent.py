import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.slack.data_model import MessageEvent
from tests.test_data import MESSAGE_AUDIO_EVENT_1, MESSAGE_EVENT_SIMPLE_1


class TestOpenAiChatAgent(unittest.TestCase):
    @patch("botchan.agents.openai_chat_agent.OPENAI_CLIENT.chat.completions.create")
    def test_process_message_no_files(self, mock_create):
        event = MESSAGE_EVENT_SIMPLE_1
        # Mocking OpenAI response
        mock_response_text = "mocked response from OpenAI"
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=mock_response_text))
        ]
        mock_create.return_value = mock_response

        agent = OpenAiChatAgent()

        response = agent.process_message(MessageEvent(**event))

        self.assertEqual(response, [mock_response_text])
        self.assertIn(f"{event['channel']}|{event['event_ts']}", agent.message_buffer)
        mock_create.assert_called_once()

    @patch("botchan.agents.openai_chat_agent.SLACK_MESSAGE_FETCHER.fetch_message")
    @patch("botchan.agents.openai_chat_agent.OPENAI_CLIENT.chat.completions.create")
    @patch("botchan.agents.openai_chat_agent.SLACK_TRANSCRIBE_WAIT_SEC", 0)
    def test_process_message_with_files(self, mock_create, mock_fetch_message):
        event = MESSAGE_AUDIO_EVENT_1
        # Mocking OpenAI response
        mock_response_text = "mocked response from OpenAI"
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=mock_response_text))
        ]
        mock_create.return_value = mock_response

        # Mocking Slack fetch message response
        mock_file_object = MagicMock()
        mock_file_object.get_transcription_preview.return_value = "transcribed text"
        mock_fetch_message.return_value = MagicMock(files=[mock_file_object])

        agent = OpenAiChatAgent(buffer_limit=2)
        response = agent.process_message(MessageEvent(**event))

        self.assertEqual(response, [mock_response_text])
        self.assertIn(f"{event['channel']}|{event['event_ts']}", agent.message_buffer)
        mock_create.assert_called_once()
        mock_fetch_message.assert_called_once()
