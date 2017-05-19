#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Poca setup"""

from distutils.core import setup


setup(
    name='poca',
    version='rev285',
    license='GPL3',
    description='a command line podcast client',
    long_description='A cron-friendly, disk-space-conscious, command line'
                     'podcast aggregator, written in Python',
    author='Mads Michelsen',
    author_email='mail@brokkr.net',
    url='https://github.com/brokkr/poca',
    scripts=['src/poca', 'src/poca-subscribe'],
    packages=['poco'],
    package_dir={'poco': 'src/poco'},
    data_files=[('share/man/man1', ["man/poca.1"])],
    requires=['feedparser', 'lxml', 'mutagen'],
    provides=['poco'],
    platforms=['POSIX'],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: POSIX',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Internet']
)
