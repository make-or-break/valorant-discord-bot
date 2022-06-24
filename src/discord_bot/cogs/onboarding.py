import imp
import discord
from discord.ext import commands
from discord.ext import tasks

import re

#from discord_bot.database.sql_statements import add_player, update_player
#from discord_bot.valorant.main import get_puuid

from ..log_setup import logger
# from ..utils import utils as ut

import valorant
from database import sql_scheme
from database import sql_statements as db


### @package misc
#
# Collection of miscellaneous helpers.
#

class Onboarding(commands.Cog):
    """
    Various useful Commands for everyone
    """

    def __init__(self, bot):
        logger.info("Onboarding cog initialized!");
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
            logger.info('Could not DM user, closed DMs.')
            exit

        logger.info(f"Onboarding DM sent to {member.name}, waiting for response.")

        def check_response(res):
            return res.channel.type == discord.ChannelType.private and res.author == member
        valid = False
        while not valid:
            response = await self.bot.wait_for('message', check=check_response)
            if (re.fullmatch(re.compile(r'\b(.{3,16}#.{3,5})\b'), response.content)):
                valid = True
            else:
                await member.send("Error: Please send a valid name and tagline in the following format: <name>#<tagline>")

        player = response.content.split('#')
        player_json = valorant.get_player_json(player[0], player[1])
        db.add_player(id=member.id, username=player[0], elo=valorant.get_elo(player_json), rank=valorant.get_rank(player_json), rank_tier=valorant.get_rank_tier(player_json), tagline=player[1], puuid=valorant.get_puuid(player_json))

        # create a new role in the guild with name get_elo(player_json) if that role does not exist
        role = discord.utils.get(member.guild.roles, name=db.get_role_by_rank_tier(valorant.get_rank_tier(player_json)).name)
        if not role:
            role = await member.guild.create_role(name=db.get_role_by_rank_tier(valorant.get_rank_tier(player_json)).name, color=discord.Color(db.get_role_by_rank_tier(valorant.get_rank_tier(player_json)).color))

        # add the role to the user
        await member.add_roles(role)
        logger.info(f"Added role {role.name} to User {member.name}!")

        await member.send("Thanks! Your Valorant Account is now connected!")

def setup(bot):
    logger.info("Onboarding cog set up!");
    bot.add_cog(Onboarding(bot))
