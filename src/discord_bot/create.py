import discord
import valorant

from .log_setup import logger


# is being executed during startup
async def roles(guild) -> None:
    """
    function makes sure all ranks defined in valorant.data.RANK_VALUE
    exist as a guild role.

    Parameters
    ----------
    guild -> guild for which roles get created

    Returns
    -------
    None
    """
    logger.info(f'Check roles for {guild}...')

    # go through all role names
    # make sure every role exists
    # reversed -> they get created in the right order
    for n in reversed(valorant.data.RANK_VALUE):

        # set role_name for readability
        role_name = valorant.data.RANK_VALUE[n]['name']

        # check if role exists - create it when not
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await guild.create_role(name=role_name, color=discord.Color.from_rgb(*valorant.data.RANK_VALUE[n]['color']),
                                    mentionable=True, hoist=True)
            logger.info(
                f"Role '{role_name}' has been created on {guild.name} - {guild.id}")


# this function is not being used in the current version
# could be useful in the future
async def channels(guild) -> None:
    """
    function makes sure all channels defined exist.

    Parameters
    ----------
    guild -> guild for which channels get created

    Returns
    -------
    None
    """

    # current state:
    # the following code would create rooms for all rank groups
    # rooms still need permissions fitting to the ranks!
    # rooms should be created within a category

    # create channels for all ranks
    for group in valorant.data.COMPETITIVE_RANK_GROUP:
        # set channel_name for readability
        channel_name = valorant.data.COMPETITIVE_RANK_GROUP[group]['name']

        # check if channel exists - create it when not
        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            await guild.create_text_channel(name=channel_name)
            logger.info(
                f"Channel '{channel_name}' has been created on {guild.name} - {guild.id}")
