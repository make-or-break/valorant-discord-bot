import discord
from discord.ext import commands
from discord.ext import tasks

import re

from ..log_setup import logger
from ..utils import utils as ut


### @package misc
#
# Collection of miscellaneous helpers.
#

class Onboarding(commands.Cog):
    """
    Various useful Commands for everyone
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # Event listener, wich does an onboarding flow if a new user is joining.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        #user = await self.client.get_user_info(member.id)
        #await self.client.send_message(user, "Welcome to the Server. Please send me your Valorant name and tagline in the following format: <name>#<tagline>")
        message = "Welcome to the Server. Please send me your Valorant name and tagline in the following format: <name>#<tagline>";
        try:
            await member.send(message)
            print(f"Onboarding DM sent to {member.name}, waiting for response.")

            def check_response(res):
                return re.search(re.compile(ur'\b(.{3,16}#.{3,5})\b'), res.content) and res.channel.type == discord.ChannelType.private and res.author == member #TODO: regex check außerhalb, wenn author und channel stimmt, um error message zu senden

            msg = await self.client.wait_for('message', check=check_response)
            print(f"Got valid response: {msg.content}")
        except:
            print('Could not DM user, closed DMs.')

def setup(bot):
    bot.add_cog(Onboarding(bot))
