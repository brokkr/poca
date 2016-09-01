# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
#  
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import argparse
from poco import version, DESCRIPTION


def get_args():
    '''Returns arguments from a command line argument parser'''
    about = "Poca " + version.__version__ + " : " + DESCRIPTION
    parser = argparse.ArgumentParser(description=about)

    parser.add_argument('-q', '--quiet', action='store_true', 
        default=False, help='Quiet mode (useful for cron jobs)')
    parser.add_argument('-l', '--logfile', action='store_true', 
        default=False, help='Output to file in poca config directory')
    parser.add_argument('-b', '--bump', action='store', 
        default=False, help='Move BUMP on to the next batch')

    return parser.parse_args()

