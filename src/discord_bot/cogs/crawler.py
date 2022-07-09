import discord
import match_crawler
import valorant
from discord.ext import commands
from discord.ext import tasks

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

    ####################################################################################################################
    # enable / disable the valorant match tracker
    # for reference: https://github.com/make-or-break/valorant-match-history
    ####################################################################################################################

    @commands.command(name='track', aliases=['tracking'])
    async def track_command(self, ctx):
        """
        This command adds the user to the tracking list.
        Once an hour, the crawler will crawl all new matches of a player.
        This Feature is opt in!
        """

        # Send Error and break if command is not executed in private chat
        if not ctx.channel.type == discord.ChannelType.private:
            await ctx.send(
                embed=ut.make_embed(
                    name='Error:',
                    value='This command is only available in private chat. Please send me a DM :)',
                    color=ut.red
                )
            )
            return

        # get corresponding puuid from db
        puuid = (db.get_player(ctx.author.id).puuid)

        # check if user allready exists in db
        if not match_crawler.user_exists(puuid):

            # add user to db in case you never enabled tracking before
            match_crawler.add_user(puuid, True)
            await ctx.send(
                embed=ut.make_embed(
                    name='add_tracking:',
                    value=f'You enabled match tracking!',
                    color=ut.green
                )
            )
            return

        else:

            # check if user is already tracked
            if match_crawler.get_tracked_status(puuid):

                # if player is getting tracked,
                # disable tracking!
                match_crawler.update_tracking(puuid, False)
                await ctx.send(
                    embed=ut.make_embed(
                        name='disable_tracking:',
                        value='You disabled match tracking!',
                        color=ut.red
                    )
                )
                return

            else:
                # if player is not tracked,
                # enable tracking!
                match_crawler.update_tracking(puuid, True)
                await ctx.send(
                    embed=ut.make_embed(
                        name='enable_tracking:',
                        value='You enabled match tracking!',
                        color=ut.green
                    )
                )
                return

    ####################################################################################################################
    # get elo stats
    # user needs to have tracking enabled
    ####################################################################################################################

    @commands.command(name='elo')
    async def elo_command(self, ctx):
        """
        send elo stats to user
        """

        # get corresponding puuid from db
        puuid = (db.get_player(ctx.author.id).puuid)

        matches = match_crawler.matches_within_time(puuid, 1)
        diff = match_crawler.get_elo_over_matches(puuid, matches)

        if diff > 0:
            color = ut.green
            diff = f'+{diff}'
        else:
            color = ut.red
            diff = f'-{diff}'

        print(diff)

        await ctx.send(
            embed=ut.make_embed(
                name='elo:',
                value=f'last 24h:\n\
                    elo: {diff}\n\
                    matches: {matches}',
                color=color
            )
        )
        return

    ####################################################################################################################

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
