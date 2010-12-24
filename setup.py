#!/usr/bin/env python
# coding=utf8

from distutils.core import setup

setup (
    name = 'tvtuner',
    version = '0.3.1',
    package_dir = {'': 'src'},
    packages = [''],
    scripts = ['src/tvtuner'],

    # Declare your packages' dependencies here, for eg:
    requires=['pylirc', 'yaml', 'aosd'],

    # Fill in these to make your Egg ready for upload to
    # PyPI
    author = 'Armin Häberling',
    author_email = 'armin.aha@gmail.com',

    description = 'TV tuner for ivtv cards.',
    license = '',
    long_description= 'Long description of the package',
)
