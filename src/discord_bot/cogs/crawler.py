import discord
import match_crawler
import valorant
from discord.ext import commands
from discord.ext import tasks
from sqlalchemy import select
from sqlalchemy import update

import database.sql_scheme as db_scheme
from ..log_setup import logger
from ..utils import utils as ut
from database import sql_statements as db


# @package misc
#
# Collection of miscellaneous helpers.
#

class Crawler(commands.Cog):
    """
    This cog crawles the Valorant-Api every 20 minutes to update the player db if something changes
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.crawler_task.start()

    @tasks.loop(minutes=20.0)
    async def crawler_task(self):
        """
        Task wich crawles the stats of the tracked players and updates the database.
        Runs every 20 minutes.
        :return: None
        """

        logger.info('Crawling players...')

        for player in db.get_all_players():

            # get player_json & check if json is valid
            if not (player_json := valorant.get_player_json_by_puuid(player.puuid)):
                logger.info(
                    f'API request for {player.username}#{player.tagline} failed - skipping')

            else:
                # rank_tier == 0 is only valid, if the player did not have a rank_tier before.
                if valorant.get_rank_tier(player_json) == 0:

                    # player still has to play its placement matches
                    if player.rank_tier is None:
                        logger.info(
                            f'{player.username}#{player.tagline} is still in placement matches')
                        # create DB entry for player
                        session = db_scheme.open_session()
                        session.query(db_scheme.Player).filter(db_scheme.Player.id == player.id).update({
                            db_scheme.Player.elo: 0,
                            db_scheme.Player.rank_tier: 0,
                            db_scheme.Player.rank: valorant.RANK_VALUE[0]['name'],
                            db_scheme.Player.username: valorant.get_name(player_json),
                            db_scheme.Player.tagline: valorant.get_tag(player_json),
                        })
                        session.commit()
                        # add role to player
                        for g in self.bot.guilds:
                            m = g.get_member(player.id)
                            if m:
                                role = discord.utils.get(
                                    g.roles, name=valorant.RANK_VALUE[0]['name'])
                                await m.add_roles(role)
                                logger.info(
                                    f'Added role {role.name} to user {m.name}!')

                    elif player.rank_tier != 0:
                        logger.info(
                            f'API request for {player.username} contains no rank_tier - skipping')

                # ONLY IS EXECUTED IF PLAYER_JSON IS VALID - insert additional checks above this line
                else:
                    rank_tier_new = valorant.get_rank_tier(player_json)
                    rank_tier_before = player.rank_tier
                    # logger.info(f'Updating {player.username} with id {player.id} in db')
                    db.update_player(id=player.id, elo=valorant.get_elo(player_json), rank=valorant.RANK_VALUE[rank_tier_new]['name'], rank_tier=rank_tier_new, username=valorant.get_name(
                        player_json), tagline=valorant.get_tag(player_json), puuid=player.puuid)
                    for g in self.bot.guilds:
                        m = g.get_member(player.id)
                        if m:
                            new_role = discord.utils.get(
                                g.roles, name=valorant.RANK_VALUE[rank_tier_new]['name'])
                            old_role = discord.utils.get(
                                g.roles, name=valorant.RANK_VALUE[rank_tier_before]['name'])
                            if not new_role:
                                new_role = await g.create_role(name=valorant.RANK_VALUE[rank_tier_new]['name'], color=discord.Color.from_rgb(*valorant.RANK_VALUE[rank_tier_new]['color']), mentionable=True, hoist=True, reason='User joint the Server and did the onboarding flow')

                            # add the role to the user
                            if new_role not in m.roles:
                                await m.remove_roles(old_role)
                                logger.info(
                                    f'Removed role {old_role.name} from user {m.name}!')
                                await m.add_roles(new_role)
                                logger.info(
                                    f'Added role {new_role.name} to user {m.name}!')
                            else:
                                pass
                                # logger.info(f'Member {m.name} already has role {new_role.name}!')

        logger.info('Crawling finished!')


async def setup(bot):
    await bot.add_cog(Crawler(bot))
