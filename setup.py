#!/usr/bin/env python
# coding=utf8

from distutils.core import setup
from distutils.extension import Extension
try:
    from Cython.Distutils import build_ext
except ImportError:
    from Pyrex.Distutils import build_ext

import commands

def pkgconfig_include_dirs(*packages):
    flag_map = {'-I': 'include_dirs'}
    kw = {}
    for token in commands.getoutput("pkg-config --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw['include_dirs']

#def pkgconfig_libraries(*packages):
#    flag_map = {'-l': 'libraries'}
#    kw = {}
#    for token in commands.getoutput("pkg-config --libs %s" % ' '.join(packages)).split():
#        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
#    return kw['libraries']
#
#def pkgconfig_library_dirs(*packages):
#    flag_map = {'-L': 'library_dirs'}
#    kw = {}
#    for token in commands.getoutput("pkg-config --libs %s" % ' '.join(packages)).split():
#        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
#    return kw['library_dirs']


setup (
    cmdclass = {'build_ext' : build_ext},

    name = 'tvtuner',
    version = '0.2.3',
    package_dir = {'': 'src'},
    packages = [''],
    ext_modules = [
        Extension(
            'aosd',
            ['src/aosd.pyx'],
            include_dirs= pkgconfig_include_dirs('pangocairo') + ['/usr/include/libaosd'],
            libraries = ['aosd', 'aosd-text']
        )
    ],
    scripts = ['src/tvtuner'],

    # Declare your packages' dependencies here, for eg:
    requires=['pylirc', 'yaml'],

    # Fill in these to make your Egg ready for upload to
    # PyPI
    author = 'Armin Häberling',
    author_email = 'armin.aha@gmail.com',

    description = 'Just another Python package for the cheese shop',
    license = '',
    long_description= 'Long description of the package',
)
