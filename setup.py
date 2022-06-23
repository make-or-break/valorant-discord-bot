from importlib.metadata import entry_points
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    install_requires=install_requires,
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
