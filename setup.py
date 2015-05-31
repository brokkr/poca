# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.

from distutils.core import setup

setup(\
name='poca', \
version='0.1.1', \
license='GPL3', \
description='a command line podcast client', \
long_description='A cron-friendly, disk-space-conscious, command line podcast aggregator, written in Python', \
author='Mads Michelsen', \
author_email='madchine@gmail.com', \
url='http://code.google.com/p/poca/', \
scripts=['src/poca'], \
packages=['poco'], \
package_dir={'poco': 'src/poco'}, \
data_files=[('share/man/man1', ["man/poca.1"]), ('/etc', ["conf/poca.example.xml"])], \
requires=['feedparser', 'urlgrabber', 'eyeD3'], \
provides=['poco'], \
platforms=['POSIX'], \
classifiers=['Development Status :: 4 - Beta', \
'Environment :: Console', \
'Intended Audience :: End Users/Desktop', \
'License :: OSI Approved :: GNU General Public License (GPL)', \
'Natural Language :: English', \
'Operating System :: POSIX', \
'Programming Language :: Python :: 2.7', \
'Topic :: Internet'] \
)


