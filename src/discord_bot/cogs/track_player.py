import discord
from discord.ext import commands
from discord.ext import tasks

from ..log_setup import logger
from ..utils import utils as ut


### @package misc
#
# Collection of miscellaneous helpers.
#

class Track_Player(commands.Cog):
    """
    Various useful Commands for everyone
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # Example for an event listener
    # This one will be called on each message the bot recieves
    @commands.Cog.listener()
    async def on_member_join(self, member):
        user = await self.client.get_user_info(member.id)
        await self.client.send_message(user, "Welcome to the Server. Please send me your Valorant name and tagline in the following format: <name>#<tagline>")
        

def setup(bot):
    bot.add_cog(Misc(bot))
