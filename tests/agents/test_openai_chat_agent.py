import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.data_model import MessageEvent
from tests.data.messages import (
    MESSAGE_AUDIO_EVENT_1,
    MESSAGE_AUDIO_EVENT_2,
    MESSAGE_EVENT_SIMPLE_1,
)


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

        agent = OpenAiChatAgent(get_message_by_event=None)

        response = agent.process_message(MessageEvent(**event))

        self.assertEqual(response, [mock_response_text])
        self.assertIn(f"{event['channel']}|{event['event_ts']}", agent.message_buffer)
        mock_create.assert_called_once()

    @patch("botchan.agents.openai_chat_agent.OPENAI_CLIENT.chat.completions.create")
    @patch("botchan.agents.openai_chat_agent.SLACK_TRANSCRIBE_WAIT_SEC", 0)
    def test_process_message_with_files(self, mock_create):
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

        get_message_by_event_mock = MagicMock(
            return_value=MessageEvent(**MESSAGE_AUDIO_EVENT_2)
        )

        agent = OpenAiChatAgent(
            get_message_by_event=get_message_by_event_mock, buffer_limit=2
        )

        response = agent.process_message(MessageEvent(**event))

        self.assertEqual(response, [mock_response_text])
        self.assertIn(f"{event['channel']}|{event['event_ts']}", agent.message_buffer)
        mock_create.assert_called_once()
