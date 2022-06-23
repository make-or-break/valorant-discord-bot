from importlib.metadata import entry_points
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='discord_bot',
    version='0.1',
    url='',
    license='',
    author='MayNiklas',
    author_email='info@niklas-steffen.de',
    description='',
    install_requires=install_requires,
    package_dir={'': 'src/'},
    packages=find_packages(where='src/'),
)
