# import os
import unittest

from botchan.agents.expert.shopping_assist import create_shopping_assist_task_graph_agent
from botchan.data_model.interface.channel import IChannel
from botchan.data_model.interface.message import IMessage


class TestTaskGraphAgent(unittest.TestCase):
    def setUp(self):
        self.agent = create_shopping_assist_task_graph_agent()

    def test_process_message(self):
        msgs = [
            "Hello",
            "Help me buy a shoe",
            "I like the black one",
            "Ok, I chose this one.",
        ]

        for idx, msg in enumerate(msgs):
            message = IMessage(
                text=msg,
                ts=432432434.4234 + idx,
                message_id=1305047132423721001,
                thread_message_id=1305047132423721001,
                channel=IChannel(id=1302791861341126737, channel_type=IChannel.Type.DM),
                attachments=None,
            )
            responses = self.agent.process_message(message_event=message)
            # print(responses)


# Run the tests
if __name__ == "__main__":
    # Set the environment variable
    # os.environ["RUN_INTEGRATION_TESTS"] = "1"
    unittest.main()