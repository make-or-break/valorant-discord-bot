from importlib.metadata import entry_points

from setuptools import find_packages
from setuptools import setup

setup(
    install_requires=[
        "requests == 2.28.0",
        "sqlalchemy == 1.4.37",
        # installing discord.py 2.0.0a via pip is not supported yet
        # using a git repository here would breake the flake as flakes are pure by definition
        # "discord.py @ git+https://github.com/Rapptz/discord.py#1335937"
    ],
    name='valorant-discord-bot',
    version='0.1',
    url='',
    license='',
    author='MayNiklas',
    author_email='info@niklas-steffen.de',
    description='',
    package_dir={'': 'src/'},
    packages=find_packages(where='src/'),
    entry_points={
        'console_scripts': [
            'valorant-discord-bot=discord_bot:start_bot',
        ]
    }
)
