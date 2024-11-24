import discord

from fluctlight.data_model.interface import IAttachment, IChannel, IMessage
from fluctlight.utt.snowflake import extract_timestamp_from_snowflake


class Adapter:
    @classmethod
    def cast_message(cls, message: discord.Message) -> IMessage:
        channel = cls.cast_channel(message.channel)
        attachments = [
            cls.cast_attachment(attachment) for attachment in message.attachments
        ]
        return IMessage(
            channel=channel,
            text=message.content,
            message_id=message.id,
            ts=extract_timestamp_from_snowflake(message.id),
            attachments=attachments,
            thread_message_id=cls.get_conversation_thread_id(message=message),
        )

    @classmethod
    def cast_channel(
        cls,
        channel: discord.Thread
        | discord.TextChannel
        | discord.DMChannel
        | discord.GroupChannel,
    ) -> IChannel:
        if isinstance(channel, discord.Thread):
            channel_type = IChannel.Type.THREAD
        elif isinstance(channel, discord.TextChannel):
            channel_type = IChannel.Type.TEXT_CHANNEL
        elif isinstance(channel, discord.DMChannel):
            channel_type = IChannel.Type.DM
        elif isinstance(channel, discord.GroupChannel):
            channel_type = IChannel.Type.GROUP
        else:
            channel_type = IChannel.Type.NOT_SUPPORT

        return IChannel(id=channel.id, channel_type=channel_type)

    @classmethod
    def cast_attachment(cls, attachment: discord.Attachment) -> IAttachment:
        return IAttachment(
            id=attachment.id,
            content_type=attachment.content_type,
            filename=attachment.filename,
            url=attachment.url,
        )

    @classmethod
    def get_conversation_thread_id(cls, message: discord.Message) -> int:
        # Check if the message is sent in a thread
        if isinstance(message.channel, discord.Thread):
            return message.channel.id
        elif isinstance(message.channel, discord.TextChannel):
            return message.id  # This could become a thread root
        elif isinstance(message.channel, discord.DMChannel):
            # DM consider all in an conversation
            return message.author.id
