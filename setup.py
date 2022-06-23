from setuptools import setup, find_packages

setup(
    name='valorant_rank_bot',
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
            'valorant_get_rank=valorant_rank_bot:get_rank',
        ],
    },
)
