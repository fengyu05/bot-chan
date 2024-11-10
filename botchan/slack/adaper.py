from botchan.data_model.interface import IAttachment, IChannel, IMessage
from botchan.data_model.slack import FileObject, MessageEvent


class Adapter:
    @classmethod
    def cast_message(cls, message: MessageEvent) -> IMessage:
        channel = cls.cast_channel(message.channel_type)
        attachments = [
            cls.cast_attachment(attachment) for attachment in message.files or []
        ]
        return IMessage(
            channel=channel,
            text=message.text,
            message_id=message.message_id,
            attachments=attachments,
            thread_message_id=message.thread_message_id,
        )

    @classmethod
    def cast_channel(cls, channel_type: str | None) -> IChannel:
        if channel_type == "im":
            channel_type = IChannel.Type.DM
        elif channel_type == "mpim":
            channel_type = IChannel.Type.GROUP
        elif channel_type == "channel":
            channel_type = IChannel.Type.TEXT_CHANNEL
        channel_type = IChannel.Type.NOT_SUPPORT

        return IChannel(channel_type=channel_type)

    @classmethod
    def cast_attachment(cls, fileobject: FileObject) -> IAttachment:
        return IAttachment(
            id=fileobject.id,
            content_type=fileobject.mimetype,
            filename=fileobject.name,
            url=fileobject.url_private_download,
        )
