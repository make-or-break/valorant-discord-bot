import discord
from discord.ext import commands
from discord.ext import tasks

from ..log_setup import logger
from ..utils import utils as ut


### @package misc
#
# Collection of miscellaneous helpers.
#

class Crawler(commands.Cog):
    """
    Various useful Commands for everyone
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # Task wich crawles the stats of the tracked players and updates the database
    # It can be started using self.my_task.start() e.g. from this cogs __init__
    @tasks.loop(seconds=60)
    async def crawler_task(self):
        print("Crawling tracked Players")

def setup(bot):
    bot.add_cog(Crawler(bot))
