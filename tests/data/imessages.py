from fluctlight.data_model.interface import IChannel, IMessage

MESSAGE_HELLO_WORLD = IMessage(
    text="Hello World!!!",
    ts=432432434.4234,
    message_id=1305047132423721001,
    thread_message_id=1305047132423721001,
    channel=IChannel(id=1302791861341126737, channel_type=IChannel.Type.DM),
    attachments=None,
)

MESSAGE_HELLO_WORLD2 = IMessage(
    text="Hello World 222",
    ts=5435434324.4324,
    message_id=1305047132423721002,
    thread_message_id=1305047132423721001,
    channel=IChannel(id=1302791861341126737, channel_type=IChannel.Type.DM),
    attachments=None,
)
