import discord.utils
from discord.emoji import Emoji
from discord.message import Message
from emoji import emojize

from fluctlight.logger import get_logger

logger = get_logger(__name__)


class DiscordReaction:
    async def add_reaction(self, message: Message, reaction_name: str) -> None:
        try:
            await message.add_reaction(
                self.parse_emoji(message=message, reaction_name=reaction_name)
            )
        except Exception as e:
            logger.error(
                f"Failed to add reaction {reaction_name} to message {message.id}: {str(e)}"
            )

    def parse_emoji(self, message: Message, reaction_name: str) -> Emoji | str:
        if message.guild:
            emoji = discord.utils.get(message.guild.emojis, name=reaction_name)
            logger.info("found guild emoji", emoji=emoji)
            if emoji is not None:
                return emoji

        # Unicode emoji
        try:
            return emojize(f":{reaction_name}:")
        except Exception as _:
            logger.warning("Unknown reaction. Replace with U+1F61C", name=reaction_name)
            return emojize("\U0001f61c")
