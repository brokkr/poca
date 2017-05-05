# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Submodule for parsing and storing cli arguments"""

import argparse
from poco import about


def get_poca_args():
    '''Returns arguments from a command line argument parser'''
    blurb = "Poca " + about.VERSION + " : " + about.DESCRIPTION
    parser = argparse.ArgumentParser(description=blurb)
    parser.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='No output to stdout (useful for cron jobs)')
    parser.add_argument('-l', '--logfile', action='store_true', default=False,
                        help='Output to file in poca config directory')
    parser.add_argument('-e', '--email', action='store_true', default=False,
                        help='Output to email (set in config)')
    parser.add_argument('-c', '--config',
                        help='Use alternate config directory')
    return parser.parse_args()

def get_poca_subscribe_args():
    '''Returns arguments from a command line argument parser'''
    blurb = "poca-subscribe " + about.VERSION + " : " + about.DESCRIPTION_SUB
    parser = argparse.ArgumentParser(description=blurb)
    parser.add_argument('-d', '--delete',
                        help='Remove subscription, delete audio files')
    parser.add_argument('-a', '--add',
                        help='Add url to list of subscriptions')
    parser.add_argument('-s', '--search',
                        help='Search for title in podcast database')
    return parser.parse_args()
