#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Poca setup"""

from distutils.core import setup


setup(
    name='poca',
    version='1.0beta14',
    license='GPL3',
    description='A fast and highly customizable command line podcast client',
    long_description=('A fast and highly customizable command line podcast '
                      'client'),
    author='Mads Michelsen',
    author_email='mail@brokkr.net',
    url='https://github.com/brokkr/poca',
    download_url='https://github.com/brokkr/poca/archive/v1.0beta14.tar.gz',
    scripts=['src/scripts/poca', 'src/scripts/poca-subscribe'],
    packages=['poca'],
    package_dir={'poca': 'src/poca'},
    data_files=[('share/man/man1', ["man/poca.1"]),
                ('share/man/man1', ["man/poca-subscribe.1"])],
    requires=['feedparser', 'lxml', 'mutagen', 'requests'],
    install_requires=['feedparser', 'lxml', 'mutagen', 'requests'],
    provides=['poca'],
    platforms=['POSIX'],
    keywords=['podcast', 'client', 'aggregator', 'cli'],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: POSIX',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Multimedia :: Sound/Audio']
)
