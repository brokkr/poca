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
    def __init__(self, success, msg = ''):
        self.success = success
        self.msg = msg

class Output:
    def __init__(self, args):
        self.log = self.get_logger(args)

    def single(self, msg):
        self.log.info(msg)

    def multi(self, msg):
        for line in msg:
            self.log.info(line)

    def cols(self, msg1, msg2):
        msg = (msg1[0:60] + ' ').ljust(63, '.') + ' ' + msg2
        self.log.info(msg)

    def head(self, msg):
        self.log.info(msg.upper())

    def cr(self):
        self.log.info('')

    def get_logger(self, args):
        logger = logging.getLogger('POCA')
        logger.setLevel(logging.INFO)
        null_handler = logging.NullHandler()
        logger.addHandler(null_handler)
        if not args.quiet:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_formatter = logging.Formatter("%(message)s")
            stream_handler.setFormatter(stream_formatter)
            logger.addHandler(stream_handler)
        return logger

    def add_filehandler(self, log_file_path):
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(file_formatter)
        self.log.addHandler(file_handler)

def colorize(_string, color):
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

