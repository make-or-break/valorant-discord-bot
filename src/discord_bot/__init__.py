import asyncio

import valorant
from .cogs import onboarding
from .main import start_bot
from .utils import utils


def main():
    asyncio.run(start_bot())


if __name__ == '__main__':
    main()
