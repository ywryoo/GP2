# -*- coding: utf-8 -*-
"""
setup.py
setup configuration for setuptools
---
Written by Yangwook Ryoo, 2017
MIT License: see LICENSE in the root directory of this source tree.
"""

from setuptools import setup

setup(
    name='gp2',
    long_description=__doc__,
    version='0.1.0',
    packages=['gp2gatherplot'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'gunicorn'
    ],
    extras_require={
        'dev': [
            'Fabric'
        ]
    },
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
