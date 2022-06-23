from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name='discord_bot',
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
            'discord_bot = discord_bot:main'
        ]
    }
)
