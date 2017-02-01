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
    if args.email:
        #email_handler = get_email_handler(prefs)
        #logger.addHandler(email_handler)
        bsmtp_handler = BufferingSMTPHandler('localhost', prefs.email['from'],
                                             prefs.email['to'], 'POCA log')
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

def get_email_handler(prefs):
    '''Adds an email handler to the logger (all sessions messages are
    gathered in memory before email is sent)'''
    smtp_handler = handlers.SMTPHandler('localhost', prefs.email['from'],
                                        prefs.email['to'], 'POCA log')
    smtp_handler.setLevel(logging.INFO)
    smtp_formatter = logging.Formatter("%(asctime)s %(message)s",
                                       datefmt='%Y-%m-%d')
    smtp_handler.setFormatter(smtp_formatter)
    memory_handler = handlers.MemoryHandler(1000, flushLevel=logging.CRITICAL,
                                            target=smtp_handler)
    return memory_handler

class BufferingSMTPHandler(handlers.BufferingHandler):
    def __init__(self, mailhost, fromaddr, toaddr, subject):
        handlers.BufferingHandler.__init__(self, 1000)
        self.mailhost = mailhost
        self.mailport = smtplib.SMTP_PORT
        self.fromaddr = fromaddr
        self.toaddr = toaddr
        self.subject = subject
        smtp_formatter = logging.Formatter("%(asctime)s %(message)s",
                                           datefmt='%Y-%m-%d %H:%M')
        self.setFormatter(smtp_formatter)

    def flush(self):
        if not len(self.buffer):
            return
        smtp = smtplib.SMTP(self.mailhost, self.mailport)
        #msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (self.fromaddr, string.join(self.toaddrs, ","), self.subject)
        msg = str()
        for record in self.buffer:
            s = self.format(record)
            msg = msg + s + "\r\n"
        smtp.sendmail(self.fromaddr, [self.toaddr], msg)
        smtp.quit()
        self.buffer = []

