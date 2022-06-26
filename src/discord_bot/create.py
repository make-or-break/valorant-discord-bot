import discord

import valorant
from .log_setup import logger


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
    logger.info(f"Check roles for {guild}...")

    # go through all role names
    # make sure every role exists
    # reversed -> they get created in the right order
    for n in reversed(valorant.data.RANK_VALUE):

        # set role_name for readability
        role_name = valorant.data.RANK_VALUE[n]["name"]

        # check if role exists - create it when not
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await guild.create_role(name=role_name, color=discord.Color.from_rgb(*valorant.data.RANK_VALUE[n]["color"]),
                                    mentionable=True, hoist=True)
            logger.info(f"Role '{role_name}' has been created on {guild.name} - {guild.id}")
