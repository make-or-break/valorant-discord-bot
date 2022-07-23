"""
Valorant discord bot
~~~~~~~~~~~~~~~~~~~
Discord bot that can be used to control valorant communities.
"""

__version__ = '0.2.0'

import asyncio

import valorant

from .cogs import onboarding
from .main import start_bot
from .utils import utils


def main():
    asyncio.run(start_bot())


if __name__ == '__main__':
    main()
