#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.


VERSION = "0.3alpha1"
MAINTAINER = "Mads Michelsen <mail@brokkr.net>"
DESCRIPTION = ("A cron-friendly, disk-space-conscious, command line podcast "
"aggregator, written in Python")
URL = "https://github.com/brokkr/poca"


import channel
import config
import files
import id3v23_frames
import history
import output

