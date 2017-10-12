# coding=UTF-8
from setuptools import setup, find_packages

setup(packages=find_packages(include=['falconratelimit', 'falconratelimit.*']),
      install_requires=["falcon", "six"],
      tests_require=[
          "nose", "mock", "coverage"
      ],
      test_suite='nose.collector'
      )
