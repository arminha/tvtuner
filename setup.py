#!/usr/bin/env python

from distutils.core import setup

setup (
    name = 'tvtuner',
    version = '0.3.1',
    package_dir = {'': 'src'},
    packages = [''],
    scripts = ['src/tvtuner'],

    requires=['pylirc', 'yaml', 'aosd'],

    author = u'Armin H\u00e4berling',
    author_email = 'armin.aha@gmail.com',

    description = 'Script to control IVTV based tv cards with an IR remote.',
    license = 'GPL',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX :: Linux'
        'Programming Language :: Python'
    ]
)
