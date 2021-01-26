#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='NAB_filter',
      version='1.0',
      packages=['NAB_filter',
                'NAB_filter.ebird',
                'NAB_filter.rules',
                'NAB_filter.inaturalist',
                ],
      install_requires=required,
     )