# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Submodule for parsing and storing cli arguments"""

import argparse
from poca import about


def get_poca_args():
    '''Returns arguments from a command line argument parser'''
    blurb = "Poca " + about.VERSION + " : " + about.DESCRIPTION
    parser = argparse.ArgumentParser(description=blurb)
    noise_level = parser.add_mutually_exclusive_group()
    noise_level.add_argument('-q', '--quiet', action='store_true',
                             default=False,
                             help='No output to stdout (useful for cron jobs)')
    noise_level.add_argument('-v', '--verbose', action='store_true',
                             default=False, help='Output details on files '
                             'being added and removed.')
    parser.add_argument('-l', '--logfile', action='store_true', default=False,
                        help='Output to file in poca config directory')
    parser.add_argument('-e', '--email', action='store_true', default=False,
                        help='Output to email (set in config)')
    parser.add_argument('-c', '--config',
                        help='Use alternate config directory')
    parser.add_argument('-t', '--threads', default=1, type=int,
                        help='Number of concurrent downloads to allow. '
                        '\'--verbose\' forces single thread.')
    return parser.parse_args()


def get_poca_subscribe_args():
    '''Returns arguments from a command line argument parser'''
    blurb = "poca-subscribe " + about.VERSION + " : " + about.DESCRIPTION_SUB
    parser = argparse.ArgumentParser(description=blurb)
    parser.add_argument('-c', '--config',
                        help='Use alternate config directory')
    subparsers = parser.add_subparsers(
        dest='cmd_name', title='commands', description='\'poca-subscribe '
        'command --help\' for futher information')
    add_parser = subparsers.add_parser('add', help='Add a new subscription '
                                       'interactively')
    list_parser = subparsers.add_parser('list',
                                        help='List current subscriptions')
    tags_parser = subparsers.add_parser('tags',
                                        help='List available id3 tags')
    del_parser = subparsers.add_parser('delete', help='Remove subscription, '
                                                      'delete files')
    del_parser.add_argument('-t', '--title',
                            help='Match against subscription title')
    del_parser.add_argument('-u', '--url',
                            help='Match against subscription url')
    toggle_parser = subparsers.add_parser('toggle', help='Set state of '
                                          'current subscriptions')
    toggle_parser.add_argument('-t', '--title',
                               help='Match against subscription title')
    toggle_parser.add_argument('-u', '--url',
                               help='Match against subscription url')
    stats_parser = subparsers.add_parser('stats', help='Get feed stats for '
                                         'current subscriptions')
    stats_parser.add_argument('-t', '--title',
                              help='Match against subscription title')
    stats_parser.add_argument('-u', '--url',
                              help='Match against subscription url')
    return parser.parse_args()
