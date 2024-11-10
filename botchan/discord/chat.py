from abc import ABC

import discord

from botchan.logger import get_logger

logger = get_logger(__name__)


class DiscordChat(ABC):
    client: discord.Client

    async def _post_message(self, channel_id: int, text: str) -> discord.Message:
        """
        Posts a message to a given Discord channel using the provided Client.

        Parameters:
            channel_id (int): The ID of the channel to which the message should be posted.
            text (str): The message content.

        Returns:
            discord.Message: The newly posted message.
        """
        channel = self.client.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel with ID {channel_id} not found.")

        message = await channel.send(content=text)
        return message

    async def send_message(self, channel_id: int, text: str) -> discord.Message:
        """
        This function sends a Discord message to the specified channel using the discord.py client.
        """
        try:
            return await self._post_message(channel_id=channel_id, text=text)
        except Exception as e:
            print(f"Error sending message: {e}")

    async def reply_to_message(
        self, message: discord.Message, thread: discord.Thread, text: str
    ) -> discord.Message:
        """
        Sends a reply to the originating channel or thread.
        """
        try:
            if thread:
                reply = await thread.send(content=text)
            else:
                reply = await message.reply(content=text)
            return reply
        except Exception as e:
            print(f"Error replying to message/thread: {e}")
