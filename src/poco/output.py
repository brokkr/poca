#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.


import logging


color_codes = { 
    'reset': '\033[0;0m',
    'bold': '\033[1m',
    'red': '\033[31m',
    'green': '\033[32m',
    'blue': '\033[34m',
    'lred': '\033[1;31m',
    'lgreen': '\033[1;32m',
    'yellow': '\033[1;33m',
    'lblue': '\033[1;34m'
    }

def colorize(_string, color):
    return color_codes[color] + str(_string) + color_codes['reset']

def get_logger(config):
    logger = logging.getLogger('POCA')
    logger.setLevel(logging.INFO)
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    if not config.args.quiet:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_formatter = logging.Formatter("%(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)
    if config.args.log_errors:
        file_handler = logging.FileHandler(config.paths.errors)
        file_handler.setLevel(logging.ERROR)
        file_formatter = logging.Formatter("%(asctime)s - %(message)s", 
            datefmt='%Y-%m-%d %H:%M')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    return logger


def print_heading(args_ns, sub_dic, i):
    '''Prints heading for each channel'''
    if not args_ns.quiet:
        if i > 0: print
        print _colorize(' '.join(sub_dic['title'].upper()), 'bold')

def print_no_news_is_good_news(args_ns):
    '''Informs user that no new entries were found in a subscription'''
    if not args_ns.quiet:
        print 'No new entries found'

def print_stats(args_ns, sub_dic, entries):
    '''Prints the categories and their number'''
    if args_ns.quiet:
        return
    for i, category in enumerate(category_synonyms):
        if i in [3,4,5,8]: continue
        no_items = len(entries[category[0]])
        print category[1].ljust(21), _colorize(no_items, category[2])


