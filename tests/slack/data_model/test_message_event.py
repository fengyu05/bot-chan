from botchan.slack.data_model import FileObject, MessageEvent
from tests.data.messages import (
    MESSAGE_AUDIO_EVENT_1,
    MESSAGE_EVENT_SIMPLE_1,
    MESSAGE_FILE_SHARE_EVENT_1,
)


def test_create_message_event():
    message_event = MessageEvent(**MESSAGE_EVENT_SIMPLE_1)
    assert message_event.user == "U0502429A8N"
    assert message_event.type == "message"
    assert message_event.ts == "1720999857.716759"
    assert message_event.client_msg_id == "6cb3204b-b615-4a07-b865-322e58140737"
    assert message_event.text == "Hello World!!!"
    assert message_event.channel == "D06C2QNN5G8"
    assert message_event.event_ts == "1720999857.716759"
    assert message_event.channel_type == "im"


def test_message_event_with_file_share_image():
    event = MessageEvent(**MESSAGE_FILE_SHARE_EVENT_1)

    assert event.type == "message"
    assert event.subtype == "file_share"
    assert event.channel == "D06C2QNN5G8"
    assert event.ts == "1721007121.115069"
    assert event.text == ""
    assert event.event_ts == "1721007121.115069"
    assert len(event.files) == 1
    file_object = event.files[0]
    assert file_object.id == "F07C9100JMB"
    assert file_object.name == "IMG_8252.jpg"
    assert file_object.mimetype == "image/jpeg"
    assert event.user == "U0502429A8N"
    assert event.is_thread_root is True
    assert event.message_id == "D06C2QNN5G8|1721007121.115069"
    assert event.thread_message_id == "D06C2QNN5G8|1721007121.115069"
    assert event.has_files is True


def test_message_event_with_payload():
    message_event = MessageEvent(**MESSAGE_AUDIO_EVENT_1)
    assert message_event.type == "message"
    assert message_event.subtype == "file_share"
    assert message_event.channel == "D06C2QNN5G8"
    assert message_event.user == "U0502429A8N"
    assert message_event.ts == "1721007506.495929"
    assert message_event.event_ts == "1721007506.495929"
    assert isinstance(message_event.files, list)
    assert len(message_event.files) == 1
    file_obj = message_event.files[0]
    assert isinstance(file_obj, FileObject)
    assert file_obj.id == "F07BYSPHHMM"
    assert file_obj.mimetype == "video/quicktime"
    assert file_obj.subtype == "slack_audio"
