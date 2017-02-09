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
import socket
from email.mime.text import MIMEText
from email.header import Header

from poco import history
from poco.outcome import Outcome


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
        self.outcome = Outcome(None, '')
        self.email = email
        smtp_formatter = logging.Formatter("%(asctime)s %(message)s",
                                           datefmt='%Y-%m-%d %H:%M')
        self.setFormatter(smtp_formatter)

    def flush(self):
        '''Flush if we exceed threshold; otherwise save the buffer'''
        if not self.buffer:
            self.outcome = Outcome(None, 'Buffer was empty')
            return
        if len(self.buffer) < self.capacity:
            self.outcome = Outcome(None, 'Buffer no sufficiently full')
            self.save()
            return
        body = str()
        for record in self.buffer:
            body = body + self.format(record) + "\r\n"
        msg = MIMEText(body.encode('utf-8'), _charset="utf-8")
        msg['From'] = self.email['fromaddr']
        msg['To'] = self.email['toaddr']
        msg['Subject'] = Header("POCA log")
        if self.email['starttls']:
            try:
                smtp = smtplib.SMTP(self.email['host'], 587, timeout=10)
                ehlo = smtp.ehlo()
            except (ConnectionRefusedError, socket.gaierror, socket.timeout) \
                    as error:
                self.outcome = Outcome(False, str(error))
                self.save()
                return
            smtp.starttls()
            try:
                smtp.login(self.email['fromaddr'], self.email['password'])
            except smtplib.SMTPAuthenticationError as error:
                self.outcome = Outcome(False, str(error))
                self.save()
                return
        else:
            try:
                smtp = smtplib.SMTP(self.email['host'], 25, timeout=10)
                ehlo = smtp.ehlo()
            except (ConnectionRefusedError, socket.gaierror, socket.timeout) \
                    as error:
                self.outcome = Outcome(False, str(error))
                self.save()
                return
        try:
            smtp.sendmail(self.email['fromaddr'], [self.email['toaddr']],
                          msg.as_string())
            self.outcome = Outcome(True, "Succesfully sent email")
        except (smtplib.SMTPException, socket.timeout) as error:
            self.outcome = Outcome(False, str(error))
            self.save()
            return
        smtp.quit()
        self.buffer = []
        self.state_jar.buffer = self.buffer
        self.state_jar.save()

    def shouldFlush(self, record):
        '''Returns false to stop automatic flushing (we flush on close)'''
        return False

    def save(self):
        '''Save the buffer for some other time (it either isn't
           full yet or we can't empty it)'''
        self.state_jar.buffer = self.buffer
        self.state_jar.save()
        self.buffer = []
