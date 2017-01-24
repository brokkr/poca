# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Create loggers needed for operation"""

import sys
import logging


def get_streamlogger(args):
    '''Gets stream logging instance'''
    logger = logging.getLogger('POCASTREAM')
    logger.setLevel(logging.INFO)
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    if not args.quiet:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_formatter = logging.Formatter("%(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

def get_summarylogger(log_file_path):
    '''Adds a filehandler to (presumed) logging instance'''
    logger = logging.getLogger('POCASUMMARY')
    logger.setLevel(logging.INFO)
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s %(message)s", 
        datefmt='%Y-%m-%d %H:%M')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

