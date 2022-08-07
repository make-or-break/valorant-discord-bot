import asyncio
from discord.ext import commands
from ..log_setup import logger


class Activity(commands.Cog):
    """
    Check activity of a user.
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # Event listener
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Check if a user has changed their activity.
        Idea: If someone starts playing a game, use that information to tell their friends.
        Important: Feature has to be opt in!
        """
        # simple test to check if we get the needed information
        logger.info(f'{after.Game.name}')


async def setup(bot):
    await bot.add_cog(Activity(bot))
