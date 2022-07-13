import discord
import match_crawler
from discord.ext import commands
from discord.ext import tasks

from ..environment import PREFIX
from ..log_setup import logger
from ..utils import utils as ut
from database import sql_statements as db


class History(commands.Cog):
    """
    This cog is responsible for the match history of a player
    """

    def __init__(self, bot):
        self.bot = bot

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

        # tell user to enable connect the valorant account first
        if not db.player_exists(ctx.author.id):
            await ctx.send(
                embed=ut.make_embed(
                    name='error:',
                    value=f'You need to first connect your Valorant account to the bot! Use the command `{PREFIX}connect`',
                    color=ut.red
                )
            )
        else:
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

        # tell user to enable connect the valorant account first
        if not db.player_exists(ctx.author.id):
            await ctx.send(
                embed=ut.make_embed(
                    name='error:',
                    value=f'You need to first connect your Valorant account to the bot! Use the command `{PREFIX}connect`',
                    color=ut.red
                )
            )
        else:
            # get corresponding puuid from db
            puuid = (db.get_player(ctx.author.id).puuid)

        if not match_crawler.user_exists(puuid):
            await ctx.send(
                embed=ut.make_embed(
                    name='Error:',
                    value=f'You need to enable match tracking first! \n\
                        Use `{PREFIX}track`',
                    color=ut.red
                )
            )
            return

        elif not match_crawler.get_tracked_status(puuid):
            await ctx.send(
                embed=ut.make_embed(
                    name='Error:',
                    value=f'You need to enable match tracking first! \n\
                        Use `{PREFIX}track`',
                    color=ut.red
                )
            )
            return

        else:
            matches = match_crawler.matches_within_time(puuid, 1)
            diff = match_crawler.get_elo_over_matches(puuid, matches)

            if diff > 0:
                color = ut.green
                diff = f'+{diff}'
            elif diff == 0:
                color = ut.yellow
                diff = f'+/-{diff}'
            else:
                color = ut.red
                diff = f'-{diff}'

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


async def setup(bot):
    await bot.add_cog(History(bot))
