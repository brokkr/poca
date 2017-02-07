# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Create loggers needed for operation"""

import logging
from logging import handlers
import smtplib
from email.mime.text import MIMEText
from poco import history


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
    return logger

def start_summarylogger(args, paths, prefs):
    '''Starts up the summary logger (for use in file and email logging)'''
    logger = get_logger('POCASUMMARY')
    logger.poca_file_handler = None
    logger.poca_email_handler = None
    if args.logfile:
        file_handler = get_file_handler(paths)
        logger.addHandler(file_handler)
        logger.poca_file_handler = file_handler
    if args.email and hasattr(prefs, 'email'):
        bsmtp_handler = BufferSMTPHandler(prefs.email, paths)
        loglevel = logging.ERROR if prefs.email['only_error'] else logging.INFO
        bsmtp_handler.setLevel(loglevel)
        logger.addHandler(bsmtp_handler)
        logger.poca_email_handler = bsmtp_handler
    return logger

def get_file_handler(paths):
    '''Adds a file handler to the logger'''
    file_handler = logging.FileHandler(paths.log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s %(message)s",
                                       datefmt='%Y-%m-%d %H:%M')
    file_handler.setFormatter(file_formatter)
    return file_handler

class BufferSMTPHandler(handlers.BufferingHandler):
    '''SMTPHandler that send one email per flush'''
    def __init__(self, email, paths):
        handlers.BufferingHandler.__init__(self, int(email['threshold']))
        self.state_jar, outcome = history.get_statejar(paths)
        self.buffer = self.state_jar.buffer
        self.email = email
        smtp_formatter = logging.Formatter("%(asctime)s %(message)s",
                                           datefmt='%Y-%m-%d %H:%M')
        self.setFormatter(smtp_formatter)

    def flush(self):
        if not len(self.buffer):
            return
        if len(self.buffer) < self.capacity:
            self.state_jar.buffer = self.buffer
            self.state_jar.save()
            self.buffer = []
            return
        smtp = smtplib.SMTP(self.email['host'], self.email['port'])
        header = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % \
                 (self.email['fromaddr'], self.email['toaddr'], 'POCA log')
        msg = str()
        for record in self.buffer:
            line = self.format(record)
            msg = msg + line + "\r\n"
        msg = MIMEText(msg.encode('utf-8'), _charset="utf-8")
        smtp.sendmail(self.email['fromaddr'], [self.email['toaddr']],
                      msg.as_string())
        smtp.quit()
        self.buffer = []
        self.state_jar.buffer = self.buffer
        self.state_jar.save()

    def shouldFlush(self, record):
        return False
