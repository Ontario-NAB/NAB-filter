#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='ebird_filter',
      version='1.0',
      packages=['ebird_filter',
                'ebird_filter.ebird',
                'ebird_filter.rules',
                'ebird_filter.inaturalist',
                ],
      install_requires=required,
     )