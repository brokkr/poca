# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import logging


class Outcome:
    '''A way to return outcome of operations in a uniform fashion'''
    def __init__(self, success, msg = ''):
        self.success = success
        self.msg = msg

def get_logger(args):
    '''Gets stream logging instance'''
    logger = logging.getLogger('POCA')
    logger.setLevel(logging.DEBUG)
    # nullhandler receives output in case of no cli or log handler
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    class WarnFilter(logging.Filter):
        def filter(self, rec):
            return rec.levelno != logging.WARN
    if not args.quiet:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_formatter = logging.Formatter("%(message)s")
        stream_handler.setFormatter(stream_formatter)
        stream_handler.addFilter(WarnFilter())
        logger.addHandler(stream_handler)

def add_filehandler(log_file_path, logger):
    '''Adds a filehandler to (presumed) logging instance'''
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s %(message)s", 
        datefmt='%Y-%m-%d %H:%M')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

def colorize(_string, color):
    '''Formatting function, adds color codes to string'''
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
    return color_codes[color] + str(_string) + color_codes['reset']

