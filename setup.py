# coding=UTF-8
from setuptools import setup, find_packages

with open('README.md', 'r') as fin:
    long_description = '\n'.join(
        x for x in fin.readlines() if not x.startswith('[!'))

from falconratelimit import __version__

setup(name='falcon-ratelimit',
      version=__version__,
      packages=find_packages(include=['falconratelimit', 'falconratelimit.*']),
      install_requires=["falcon", "six"],
      tests_require=[
          "nose", "mock", "coverage", "freezegun"
      ],
      test_suite='nose.collector',
      long_description=long_description,
      description='A rate limiter plugin for Falcon'
      )
