#!/usr/bin/env python

# Copyright (c) 2018 Brett Whitelaw
# All rights reserved.
# Unauthorized redistribution prohibited.

"""InstaMax setup.py.

:Author: Brett Whitelaw (GitHub: bwhitela)
:Date: 2018/05/14
:Last Update: 2018/05/14
"""

import sys

from setuptools import setup
from setuptools import find_packages


version = '1.0.0'

install_requires = [
    'Pillow==6.2.1'
]


setup(name='InstaMax',
      version=version,
      description="Maximize Image Size for Instagram",
      long_description="See the README.rst file.",
      keywords='instagram web picture image imageProcessing',
      author='Brett Whitelaw',
      author_email='brett.whitelaw@me.com',
      url='http://instamax.brettwhitelaw.com/',
      license='BSD 2-Clause "Simplified" License',
      packages=find_packages(),
      install_requires=install_requires,
      )
