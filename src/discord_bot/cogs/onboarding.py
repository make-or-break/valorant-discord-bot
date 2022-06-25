import imp
import discord
from discord.ext import commands
from discord.ext import tasks

import re


from ..log_setup import logger
from ..utils import utils as ut

import valorant
from database import sql_statements as db


### @package onboarding
#
# Onboarding flow to connect Valorant accounts with Discord users
#

class Onboarding(commands.Cog):
    """
    Onboarding flow and command to connect Valorant accounts with Discord users
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
        except Exception as ex:
            logger.info(f"Something went wrong: {ex.message}")
            return

        logger.info(f"Onboarding DM sent to {member.name}, waiting for response.")

        #TODO: extract onboarding flow to method for access from here and the manual onboarding command
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

        if not db.player_exists(member.id):
            db.add_player(id=member.id, elo=valorant.get_elo(player_json), rank=valorant.RANK_VALUE[valorant.get_rank_tier(player_json)]["name"], rank_tier=valorant.get_rank_tier(player_json), username=player[0], tagline=player[1], puuid=valorant.get_puuid(player_json))
            logger.info(f"Added player {player[0]}#{player[1]} to database.")
        else:
            db.update_player(id=member.id, elo=valorant.get_elo(player_json), rank=valorant.RANK_VALUE[valorant.get_rank_tier(player_json)]["name"], rank_tier=valorant.get_rank_tier(player_json), username=player[0], tagline=player[1], puuid=valorant.get_puuid(player_json))
            logger.info(f"Updated player {player[0]}#{player[1]} in database.")

        # create a new role in the guild with name get_elo(player_json) if that role does not exist
        role = discord.utils.get(member.guild.roles, name=valorant.RANK_VALUE[valorant.get_rank_tier(player_json)]["name"])
        if not role:
            role = await member.guild.create_role(name=valorant.RANK_VALUE[valorant.get_rank_tier(player_json)]["name"], color=discord.Color.from_rgb(*valorant.RANK_VALUE[valorant.get_rank_tier(player_json)]["color"]), mentionable = True, hoist = True, reason = "User joint the Server and did the onboarding flow")

        # add the role to the user
        await member.add_roles(role)
        logger.info(f"Added role {role.name} to user {member.name}!")

        await member.send("Thanks! Your Valorant Account is now connected!")

    #TODO: Add event listener for command to start onboarding flow manually

def setup(bot):
    bot.add_cog(Onboarding(bot))
