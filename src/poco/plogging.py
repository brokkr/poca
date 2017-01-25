# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Create loggers needed for operation"""

import logging


def get_logger(logger_name):
    '''Initialises and returns a basic, generic logger'''
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)
    return logger

def start_streamlogger(args):
    '''Starts up a stream logger'''
    logger = get_logger('POCASTREAM')
    if not args.quiet:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_formatter = logging.Formatter("%(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

def start_summarylogger(args, log_file_path):
    '''Starts up the summary logger (for use in file and email logging)'''
    logger = get_logger('POCASUMMARY')
    if args.logfile:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter("%(asctime)s %(message)s",
                                           datefmt='%Y-%m-%d %H:%M')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # if args.smtp
    # specify an smtphandler
    # specify memoryhandler (with smpthandler as target)
    # yes to flushonclose
    # set a high enough buffer (number of entries) that it will not trigger
    # close memoryhandler after sub loop, flushing the buffer
    # (note: this will probably also flush and empty buffer...)

    # smtp_handler = logging.handlers.SMTPHandler('localhost', 'mads@localhost', 'mads@localhost', 'Oops!')
    # smtp_formatter = logging.Formatter("%(asctime)s %(message)s", datefmt='%Y-%m-%d %H:%M')
    # smtp_handler.setLevel(logging.INFO)
    # logger.addHandler(smtp_handler)
