# -*- coding: utf-8 -*-
"""
setup.py
setup configuration for setuptools
---
Written by Yangwook Ryoo, 2017
MIT License: see LICENSE at root directory
"""

from setuptools import setup

setup(
    name='Graduation Project 2',
    long_description=__doc__,
    version='0.1.0',
    packages=['gp2-core'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'gunicorn'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
