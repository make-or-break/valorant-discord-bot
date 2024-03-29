import time
from datetime import datetime

import discord
import match_crawler
import valorant
from discord.ext import commands
from discord.ext import tasks

from ..environment import PREFIX
from ..log_setup import logger
from ..utils import utils as ut
from database import sql_statements as db


class History(commands.Cog):
    """
    Match History features:
    get some basic statistics abouut your performance in ranked!
    """

    def __init__(self, bot):
        self.bot = bot

    ####################################################################################################################
    # enable / disable the valorant match tracker
    # for reference: https://github.com/make-or-break/valorant-match-history
    ####################################################################################################################

    # TODO: obsolete when !settings is implemented
    @commands.command(name='track', aliases=['tracking'])
    async def track_command(self, ctx):
        """
        This command toggles the tracking option.
        When enabled, the crawler will crawl all new matches every 15 minutes.
        It's needed for the '!elo' command.
        Your match history will be saved in the database.
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

    @commands.command(name='demo')
    async def demo_command(self, ctx, arg=None):

        if arg is None:
            logger.info(f'no arg')

            await ctx.send(
                embed=ut.make_embed(
                    name='no arg:',
                    value=f'no argument',
                    color=ut.red
                )
            )

        else:
            logger.info(f'arg: {arg}')

            await ctx.send(
                embed=ut.make_embed(
                    name='arg:',
                    value=f'argument: {arg}',
                    color=ut.red
                )
            )

            if ctx.message.mentions == []:
                logger.info(f'no mention')

                await ctx.send(
                    embed=ut.make_embed(
                        name='no mention:',
                        value=f'no mention',
                        color=ut.red
                    )
                )

            else:
                logger.info(f'mention: {ctx.message.mentions[0]}')

                await ctx.send(
                    embed=ut.make_embed(
                        name='mention:',
                        value=f'mention: {ctx.message.mentions[0]}',
                        color=ut.red
                    )
                )

    # TODO: add option to get elo of other user (when he has public elo enabled)

    @commands.command(name='elo')
    async def elo_command(self, ctx, arg=None):
        """
        Receive some basic statistics about your performance in ranked.
        Data will be updated every 15 minutes.
        Tracking needs to be enabled.
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
            # get corresponding player from db
            player = db.get_player(ctx.author.id)

            # when user is being mentioned
            # get the mentioned user

            if arg is not None and ctx.message.mentions[0]:
                user = ctx.message.mentions[0]
                player = db.get_player(user.id)

            # only continue if user has elo value
            if (elo := player.elo) is None:
                await ctx.send(
                    embed=ut.make_embed(
                        name='error:',
                        value=f'You have no elo stats yet!',
                        color=ut.red
                    )
                )
                return

            rank = valorant.RANK_VALUE[(player.rank_tier)]['name']
            next_rank = valorant.RANK_VALUE[(player.rank_tier)+1]['name']

            # mod 100
            elo_needed = 100-(int(elo) % 100)

        if not match_crawler.user_exists(player.puuid):
            await ctx.send(
                embed=ut.make_embed(
                    name='Error:',
                    value=f'You need to enable match tracking first! \n\
                        Use `{PREFIX}track`',
                    color=ut.red
                )
            )
            return

        elif not match_crawler.get_tracked_status(player.puuid):
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

            days = 10

            # seconds = days * 24 * 60 * 60
            # compare_to = time.time() - seconds
            # matches_total = len(
            #     match_crawler.get_matches_by_puuid(player.puuid)
            # )
            # oldest_match_date = int(
            #     match_crawler.get_match_date(player.puuid, matches_total))

            # if player.puuid == '':
            #     matches = matches_total
            #     match_elo = match_crawler.get_match_last(
            #         player.puuid, matches).match_elo
            #     logger.info(f'{match_elo}')

            # else:

            matches = match_crawler.matches_within_time(player.puuid, days)
            
            logger.info(f'{player.username}#{player.tagline} - {matches} matches within the last {days} days')

            if matches > 0:
                diff = match_crawler.get_elo_over_matches(player.puuid, matches)
                logger.info(f'{player.username}#{player.tagline} - {diff} elo diff within the last {days} days')
                wins, losses = match_crawler.get_wins_losses(player.puuid, matches)
                logger.info(f'{player.username}#{player.tagline} - {wins} wins and {losses} losses within the last {days} days')
                best_elo_match_season = match_crawler.get_highest_elo_match_season(player.puuid)
                logger.info(f'{player.username}#{player.tagline} - {best_elo_match_season.match_elo} elo in best match within the last {days} days')
            else:
                diff, wins, losses, best_elo_match_season = 0, 0, 0, 0

            best_elo_match = match_crawler.get_highest_elo_match(player.puuid)

            if diff > 0:
                color = ut.green
                diff = f'+{diff}'
            elif diff == 0:
                color = ut.yellow
                diff = f'+/-{diff}'
            else:
                color = ut.red
                diff = f'{diff}'

            # act info
            season, season_name, act_end = valorant.current_season()

            if arg is not None and ctx.message.mentions[0]:
                user_mention = user.mention
            else:
                user_mention = ctx.author.mention

            if matches > 0:
                await ctx.send(
                    embed=ut.make_embed(
                        name='elo:',
                        value=(
                            f'{user_mention} ({player.username}#{player.tagline}) within the last {days} days:\n'
                            f'diff: {diff} RR\n'
                            f'matches: {matches} ({wins}W/{losses}L)\n'
                            f'rank: {rank} ({elo} RR)\n'
                            f'next rank: {next_rank} ({elo_needed} RR needed)\n'
                            f'{season_name} ends in {int(valorant.act_left()/60/60)} hours ({datetime.fromtimestamp(act_end).strftime("%m/%d/%Y, %H:%M:%S")})'
                            f'\n'
                            f'--------\n'
                            f'records:\n'
                            f'highest this season: {best_elo_match_season.match_elo} RR - {valorant.get_name_rank_rr(best_elo_match_season.match_elo)} ({datetime.fromtimestamp(match_crawler.get_end_of_match(best_elo_match_season)).strftime("%m/%d/%Y, %H:%M:%S")})\n'
                            f'highest all time: {best_elo_match.match_elo} RR - {valorant.get_name_rank_rr(best_elo_match.match_elo)} ({datetime.fromtimestamp(match_crawler.get_end_of_match(best_elo_match)).strftime("%m/%d/%Y, %H:%M:%S")})\n'
                        ),
                        color=color
                    )
                )
            else:
                await ctx.send(
                    embed=ut.make_embed(
                        name='elo:',
                        value=(
                            f'{user_mention} ({player.username}#{player.tagline}):\n'
                            f'rank: {rank} ({elo} RR)\n'
                            f'next rank: {next_rank} ({elo_needed} RR needed)\n'
                            f'--------\n'
                            f'records:\n'
                            f'highest all time: {best_elo_match.match_elo} RR - {valorant.get_name_rank_rr(best_elo_match.match_elo)} ({datetime.fromtimestamp(match_crawler.get_end_of_match(best_elo_match)).strftime("%m/%d/%Y, %H:%M:%S")})\n'
                        ),
                        color=color
                    )
                )


            # # delete command message
            # if arg is None:
            #     await ctx.message.delete()
            return


async def setup(bot):
    await bot.add_cog(History(bot))
