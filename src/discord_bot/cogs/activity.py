import asyncio

import discord
from discord.ext import commands

from ..log_setup import logger


class Activity(commands.Cog):
    """
    Check activity of a user.
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # Listener for presence updates
    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """
        Check if a user has changed their activity.
        Idea: If someone starts playing a game, use that information to tell their friends.
        Important: Feature has to be opt in!
        """
        # simple test to check if we get the needed information

        # TODO: Add opt-in

        # catch case that only members' status (online, offline, ...) changed
        if before.activities == after.activities:
            logger.debug(f"Status of '{after.name}#{after.discriminator}' ({after.id}) changed, no activity change")
            return

        logger.info(
            f"Activity of '{after.name}#{after.discriminator}' ({after.id}) changed:\n"
            f"{before.activities} ->\n"
            f"{after.activities}")


async def setup(bot):
    await bot.add_cog(Activity(bot))
