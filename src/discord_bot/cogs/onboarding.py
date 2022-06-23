import imp
from turtle import update
import discord
from discord.ext import commands
from discord.ext import tasks

import re

from discord_bot.database.sql_statements import update_player

from ..log_setup import logger
from ..utils import utils as ut

from ..valorant import *
from ..database import *


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
        except:
            print('Could not DM user, closed DMs.')
            exit

        print(f"Onboarding DM sent to {member.name}, waiting for response.")

        def check_response(res):
            return res.channel.type == discord.ChannelType.private and res.author == member #TODO: regex check außerhalb, wenn author und channel stimmt, um error message zu senden

        valid = False
        while not valid:
            response = await self.client.wait_for('message', check=check_response)
            if (re.search(re.compile(ur'\b(.{3,16}#.{3,5})\b'), response.content)):
                valid = True
            else:
                await member.send("Error: Please send a valid name and tagline in the following format: <name>#<tagline>")

        player = response.split('#')
        player_json = get_player_json(get_player_json(player[0], player[1]))
        update_player("id", get_elo(player_json), get_rank(player_json), get_rank_tier(player_json), player[0], player[1])

        await member.send("Thanks! Your Valorant Account is now connected!")

def setup(bot):
    bot.add_cog(Onboarding(bot))
