# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import sys
import logging


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

