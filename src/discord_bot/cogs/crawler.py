import discord
from discord.ext import commands
from discord.ext import tasks

import valorant
from ..log_setup import logger
from ..utils import utils as ut
from database import sql_statements as db


### @package misc
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

    # Task wich crawles the stats of the tracked players and updates the database
    @tasks.loop(minutes=20.0)
    async def crawler_task(self):
        logger.info('Crawling players...')
        for player in db.get_all_players():
            logger.info(f'Crawling {player.username}...')
            player_json = valorant.get_player_json_by_puuid(player.puuid)
            rank_tier_new = valorant.get_rank_tier(player_json)
            rank_tier_before = player.rank_tier
            logger.info(f'Updating {player.username} with id {player.id} in db')
            db.update_player(id=player.id, elo=valorant.get_elo(player_json), rank=valorant.RANK_VALUE[rank_tier_new]['name'], rank_tier=rank_tier_new, username=valorant.get_name(player_json), tagline=valorant.get_tag(player_json), puuid=player.puuid)
            for g in self.bot.guilds:
                m = g.get_member(player.id)
                if m:
                    new_role = discord.utils.get(g.roles, name=valorant.RANK_VALUE[rank_tier_new]['name'])
                    old_role = discord.utils.get(g.roles, name=valorant.RANK_VALUE[rank_tier_before]['name'])
                    if not new_role:
                        new_role = await g.create_role(name=valorant.RANK_VALUE[rank_tier_new]['name'], color=discord.Color.from_rgb(*valorant.RANK_VALUE[rank_tier_new]['color']), mentionable = True, hoist = True, reason = 'User joint the Server and did the onboarding flow')

                    # add the role to the user
                    if new_role not in m.roles:
                        await m.remove_roles(old_role)
                        logger.info(f'Removed role {old_role.name} from user {m.name}!')
                        await m.add_roles(new_role)
                        logger.info(f'Added role {new_role.name} to user {m.name}!')
                    else:
                        logger.info(f'Member {m.name} already has role {new_role.name}!')
        logger.info('Crawling finished!')


async def setup(bot):
    await bot.add_cog(Crawler(bot))
