import discord
import valorant

from .log_setup import logger


async def give_unregistered_role(member) -> None:
    """
    function makes sure user has the unregistered guild role.

    Parameters
    ----------
    member -> member receiving the role

    Returns
    -------
    None
    """

    logger.info(f"Adding role 'unregistered' to {member.name}...")

    try:

        # get role object
        role = discord.utils.get(member.guild.roles, name='unregistered')

        # only add role if it user does not have it yet
        if role in member.roles:
            logger.info(f"{member.name} already has the role 'unregistered'.")
            return

        try:
            await member.add_roles(role)
            logger.info(f"Added role 'unregistered' to {member.name}.")

        except Exception as ex:
            logger.error(
                f"Failed to add role 'unregistered' to {member.name}.")

    except Exception as ex:
        logger.info(
            f"Something went wrong getting role 'unregistered' or roles of user {member.name}: {ex.message}")
        return


async def remove_unregistered_role(member) -> None:
    """
    function makes sure user has NOT unregistered guild role.

    Parameters
    ----------
    member -> member role gets removed from

    Returns
    -------
    None
    """

    logger.info(f"Removing role 'unregistered' from {member.name}...")

    try:

        # get role object
        role = discord.utils.get(member.guild.roles, name='unregistered')

        # only remove role if user does have it
        if role not in member.roles:
            logger.info(
                f"{member.name} does not have the role 'unregistered'.")
            return

        try:
            await member.remove_roles(role)
            logger.info(f"Removed role 'unregistered' from {member.name}.")
            return

        except Exception as ex:
            logger.error(
                f"Failed to remove role 'unregistered' from {member.name}.")
            return

    except Exception as ex:
        logger.info(
            f"Something went wrong getting role 'unregistered' or roles of user {member.name}: {ex.message}")
        return
