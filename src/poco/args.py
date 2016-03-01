#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import argparse
from poco import VERSION, DESCRIPTION


def get_args():
    '''Returns arguments from a command line argument parser'''
    about = "Poca " + VERSION + " : " + DESCRIPTION
    parser = argparse.ArgumentParser(description=about)

    parser.add_argument('-q', '--quiet', action='store_true', 
        default=False, help='Quiet mode (useful for cron jobs)')
    parser.add_argument('-e', '--log-errors', action='store_true', 
        default=False, help='Log errors to file in poca config directory')
    parser.add_argument('-r', '--restart', action='store_true', 
        default=False, help=('Delete all created directories with contents '
        'plus log file and start over'))

    return parser.parse_args()

