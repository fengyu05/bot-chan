import discord

from botchan.logger import get_logger
from botchan.settings import DISCORD_BOT_GUILD_ID

logger = get_logger(__name__)


class DiscordGuild:
    client: discord.Client

    def get_guild(self, guild_id: int) -> discord.Guild:
        return self.client.get_guild(guild_id)

    def get_bot_guild(self) -> discord.Guild:
        return self.get_guild(guild_id=DISCORD_BOT_GUILD_ID)

    def get_message_author_member(
        self, message: discord.Message
    ) -> discord.Member | None:
        """It will always return None, if intents.member is not enable."""
        guild = self.get_bot_guild()
        assert guild, "Bot guild doesn't exist"
        return guild.get_member(message.author.id)
