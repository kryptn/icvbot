"""
Installation
===============

python setup.py develop 

We suggest running in a virtualenv

Run Bot
================

python icvbot.py --help


"""

from setuptools import setup, find_packages

requires = [
    'mysql-python',
    'twisted',
]

setup( 
    name='icvbot',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires = requires,
)

