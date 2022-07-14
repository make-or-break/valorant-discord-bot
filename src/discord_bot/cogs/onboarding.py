import asyncio
import re

import discord
from discord.ext import commands
from sqlalchemy import null

import valorant
from ..environment import PREFIX
from ..log_setup import logger
from ..utils import utils as ut
from database import sql_statements as db


# Button View for canceling the current dialog
class CancelView(discord.ui.View):

    def __init__(self, *, timeout=None, target=None, message_list=[]):
        super().__init__(timeout=timeout)
        self.target=target
        self.message_list=message_list

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if (not self.target.cancelled()) and (not self.target.done()):
            self.target.cancel()
            logger.info(f'Cancelled: {self.target}')

        # Disable clicked button
        button.disabled=True
        button.label='Cancelled!'
        await interaction.response.edit_message(view=self)

        # Disable all other buttons connected to the same dialog
        for message in self.message_list:
            await message.edit(view=self)


# Button View for changing account in db
class ChangeAccountView(discord.ui.View):

    def __init__(self, *, timeout=None, user, bot, message_list=[]):
        super().__init__(timeout=timeout)
        self.user=user
        self.bot=bot
        self.message_list=message_list


    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes_button(self, interaction:discord.Interaction, child:discord.ui.Button):
        # Disable buttons
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(view=self)

        try:
            message = await self.user.send(
                embed=ut.make_embed(
                    name='Change your Account',
                    value='Please send me your new Valorant name and tagline in the following format: <name>#<tagline>, to change your Valorant account.',
                    color=ut.blue_light
                ),
                view = CancelView(target = asyncio.current_task(asyncio.get_running_loop()), message_list=self.message_list)
            )
            self.message_list.append(message)

        except Exception as ex:
            logger.info(f'Something went wrong: {ex.message}')
            return

        logger.info(f'Change account DM sent to {self.user.name}, waiting for response.')
        response = await validate_name(self, user=self.user, message_list=self.message_list)
        player = response.content.split('#')
        player_json = valorant.get_player_json(player[0], player[1])

        rank_tier_before = db.get_player(id=self.user.id).rank_tier
        rank_tier_new = valorant.get_rank_tier(player_json)
        db.update_player(id=self.user.id, elo=valorant.get_elo(player_json), rank=valorant.RANK_VALUE[rank_tier_new]['name'], rank_tier=rank_tier_new, username=player[0], tagline=player[1], puuid=valorant.get_puuid(player_json))

        await self.user.send(
            embed=ut.make_embed(
                name='Success',
                value='You were added to the db.',
                color=ut.green
            )
        )

        for g in self.bot.guilds:
            m = g.get_member(self.user.id)
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


    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no_button(self, interaction:discord.Interaction, child:discord.ui.Button):
        # Disable buttons
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(view=self)


# Button View for changing settings
class SettingsView(discord.ui.View):

    public = False

    def __init__(self, *, timeout=None, user, bot):
        super().__init__(timeout=timeout)
        self.user=user
        self.bot=bot
        self.settings=db.get_settings(id=self.user.id)
        SettingsView.public = self.settings.elo_public

    #TODO: move enable/disable tracking from match history cog to here
    @discord.ui.button(label='Tracking: Off', style=discord.ButtonStyle.red)
    async def tracking_button(self, interaction:discord.Interaction, child:discord.ui.Button):
        pass

    @discord.ui.button(label=f"Elo: {'public' if public else 'private'}", style=discord.ButtonStyle.green if public else discord.ButtonStyle.red)
    async def elo_button(self, interaction:discord.Interaction, child:discord.ui.Button):
        if self.settings.elo_public:
            db.update_settings(id=self.user.id, elo_public=False)
            child.label='Elo: private'
            child.style=discord.ButtonStyle.red
            self.settings = db.get_settings(id=self.user.id)
            logger.info(f'elo_public set to: {self.settings.elo_public}')
            
        else:
            db.update_settings(id=self.user.id, elo_public=True)
            child.label='Elo: public'
            child.style=discord.ButtonStyle.green
            self.settings = db.get_settings(id=self.user.id)
            logger.info(f'elo_public set to: {self.settings.elo_public}')
            
        await interaction.response.edit_message(view=self)


#TODO: add admin commands: remove player from db, add player to db by admin.

### @package onboarding
#
# Onboarding flow to connect Valorant accounts with Discord users
#

class Onboarding(commands.Cog):
    """
    Onboarding flow and command to connect Valorant accounts with Discord users.
    """

    #TODO: deactivate receiving commands while onboarding is active

    def __init__(self, bot):
        self.bot: commands.Bot = bot


    async def add_db_entry(self, user, player):
        player_json = valorant.get_player_json(player[0], player[1])
        db.add_player(id=user.id, elo=valorant.get_elo(player_json), rank=valorant.RANK_VALUE[valorant.get_rank_tier(player_json)]['name'], rank_tier=valorant.get_rank_tier(player_json), username=player[0], tagline=player[1], puuid=valorant.get_puuid(player_json))
        logger.info(f'Added player {player[0]}#{player[1]} to database.')


    async def add_role(self, member, rank_tier):
        # create a new role in the guild with name get_rank_tier(player_json) if that role does not exist
        role = discord.utils.get(member.guild.roles, name=valorant.RANK_VALUE[rank_tier]['name'])
        if not role:
            role = await member.guild.create_role(name=valorant.RANK_VALUE[rank_tier]['name'], color=discord.Color.from_rgb(*valorant.RANK_VALUE[rank_tier]['color']), mentionable = True, hoist = True, reason = 'User joint the Server and did the onboarding flow')

        # add the role to the user
        if role not in member.roles:
            await member.add_roles(role)
            logger.info(f'Added role {role.name} to user {member.name}!')
        else:
            logger.info(f'Member {member.name} already has role {role.name}!')
        return role


    #TODO: Überprüfung mit "Ist das wirklich dein Account - Ja - Nein - nach connecten"
    @commands.command(name='connect', help='Connect your Valorant account to your Discord account')
    async def connect(self, ctx, *params):
        """!
        Connect your Valorant Account to your Discord account. If you are already connected you can use this command to change the connected account.
        @param ctx Context of the message
        @param params further arguments
        """

        message_list = []

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

        # If player already exists in db add role on all his guilds managed by this bot, otherwise start the onboarding first
        if not db.player_exists(ctx.author.id):
            # Valorant name not in params -> Ask for name
            if not params:
                try:

                    message = await ctx.send(
                        embed=ut.make_embed(
                            name='Connect your Account',
                            value='Please send me your Valorant name and tagline in the following format: <name>#<tagline>, to connect your Valorant account.',
                            color=ut.blue_light
                        ),
                        view = CancelView(target = asyncio.current_task(asyncio.get_running_loop()), message_list=message_list)
                    )
                    message_list.append(message)

                except Exception as ex:
                    logger.info(f'Something went wrong: {ex.message}')
                    return

                logger.info(f'Connect account DM sent to {ctx.message.author.name}, waiting for response.')

                response = await validate_name(self, user=ctx.message.author, message_list=message_list)
                player = response.content.split('#')
                await self.add_db_entry(user=ctx.message.author, player=player)

                await ctx.send(
                    embed=ut.make_embed(
                        name='Success',
                        value='You were added to the db.',
                        color=ut.green
                    )
                )

            # Valorant name in params
            else:
                if not (re.fullmatch(re.compile(r'\b(.{3,16}#.{3,5})\b'), params[0])):
                    message = await ctx.send(
                        embed=ut.make_embed(
                            name='Error: Thats not a valid name and tagline.',
                            value='Please resend a valid name and tagline in the following format: <name>#<tagline> in a message.',
                            color=ut.red
                        ),
                        view = CancelView(target = asyncio.current_task(asyncio.get_running_loop()), message_list=message_list)
                    )
                    message_list.append(message)

                    response = await validate_name(self, user=ctx.message.author, message_list=message_list)

                    player = response.content.split('#')
                    await self.add_db_entry(user=ctx.message.author, player=player)
                else:
                    player = params[0].split('#')
                    await self.add_db_entry(user=ctx.message.author, player=player)

                await ctx.send(
                    embed=ut.make_embed(
                        name='Success',
                        value='You were added to the db.',
                        color=ut.green
                    )
                )

        # Player already in db
        else:
            await ctx.send(
                embed=ut.make_embed(
                    name='Info:',
                    value='Your account is already connected.\n Do you want to change it?',
                    color=ut.blue_light
                ),
                view = ChangeAccountView(user=ctx.message.author, bot=self.bot, message_list=message_list)
            )

        for g in self.bot.guilds:
            m = g.get_member(ctx.message.author.id)
            if m:
                await self.add_role(member=m, rank_tier=db.get_player(ctx.author.id).rank_tier)


    # Event listener, wich does an onboarding flow if a new user is joining.
    @commands.Cog.listener()
    async def on_member_join(self, member):

        message_list = []

        # if player is already in the db (onbording done on other guild) just add the role, otherwise start the onboarding
        if not db.player_exists(member.id):
            try:
                message = await member.send(
                    embed=ut.make_embed(
                        name=f'Welcome {member.name}',
                        value=f'Welcome to the {member.guild.name} Server. Please send me your Valorant name and tagline in the following format: <name>#<tagline>',
                        color=ut.green
                    ),
                    view=CancelView(target = asyncio.current_task(asyncio.get_running_loop()), message_list=message_list)
                )
                message_list.append(message)

            except Exception as ex:
                logger.info(f'Something went wrong: {ex.message}')
                return

            logger.info(f'Onboarding DM sent to {member.name}, waiting for response.')

            response = await validate_name(self, user=member, message_list=message_list)

            player = response.content.split('#')
            await self.add_db_entry(user=member, player=player)
            role = await self.add_role(member=member, rank_tier=db.get_player(member.id).rank_tier)
            await member.send(
                embed=ut.make_embed(
                    name='Info',
                    value=f'I gave you your matching role: {role.name}',
                    color=ut.green
                )
            )
        else:
            role = await self.add_role(member=member, rank_tier=db.get_player(member.id).rank_tier)
            await member.send(
                embed=ut.make_embed(
                    name=f'Welcome {member.name}',
                    value=f'Welcome to the {member.guild.name} Server. I gave you your matching role: {role.name}',
                    color=ut.green
                )
            )


    # Event listener, wich does an onboarding flow if a new user is joining.
    @commands.command(name='settings', help='Change your settings.')
    async def settings(self, ctx):
        """!
        Change your settings.
        @param ctx Context of the message
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

        # If player already exists in db add role on all his guilds managed by this bot, otherwise start the onboarding first
        if not db.settings_exists(ctx.author.id):
            if not db.player_exists(ctx.author.id):
                await ctx.send(
                    embed=ut.make_embed(
                        name='Error:',
                        value=f'You have to connect your Valorant account first. Please use the command `{PREFIX}connect`.',
                        color=ut.red
                    )
                )
                return
            else:
                db.add_settings(ctx.author.id)
                logger.info(f'Settings created in db for {ctx.author.name}')
        
        await ctx.send(
                embed=ut.make_embed(
                    name='Settings:',
                    value=f'Tracking: enable match tracking (necessary for the `{PREFIX}elo` command).\n Elo: allow others to use `{PREFIX}elo` to get your stats. (if private, only you can use it)\n\n Click the buttons to toggle the settings. (Button label is the current state)',
                    color=ut.blue_light
                ),
                view=SettingsView(user=ctx.author, bot=self.bot)
            )


async def validate_name(self, user, message_list=[]):
    def check_response(res):
        return res.channel.type == discord.ChannelType.private and res.author == user
    valid = False
    while not valid:
        response = await self.bot.wait_for('message', check=check_response)
        if (re.fullmatch(re.compile(r'\b(.{3,16}#.{3,5})\b'), response.content)):
            valid = True
        else:
            message = await user.send(
                embed=ut.make_embed(
                    name='Error:',
                    value='Please send a valid name and tagline in the following format: <name>#<tagline>',
                    color=ut.red
                ),
                view=CancelView(target = asyncio.current_task(asyncio.get_running_loop()), message_list=message_list)
            )
            message_list.append(message)
    return response


async def setup(bot):
    await bot.add_cog(Onboarding(bot))
