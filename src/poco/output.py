# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.


import logging


logger = logging.getLogger('POCA')

# config reporting
def conffatal(msg):
    logger.fatal(msg)

def confinfo(msg):
    logger.info(msg)

# subscription error reporting
def subfatal(title, outcome):
    err = "\N{Heavy Exclamation Mark Symbol}"
    logger.fatal(title + '. ' + err + 'FATAL' + err + ' ' + outcome.msg)

def suberror(title, outcome):
    err = "\N{Heavy Exclamation Mark Symbol}"
    logger.error(title + '. ' + err + 'ERROR' + err + ' ' + outcome.msg)

# report on intentions based on analysis
def plans(title, no_unwanted, no_lacking):
    msg = title
    if no_unwanted > 0 or no_lacking > 0:
        msg = msg + '. '
    if no_unwanted > 0:
        msg = msg + str(no_unwanted) + ' ' + "\N{HEAVY MINUS SIGN}" 
    if no_unwanted > 0 and no_lacking > 0:
        msg = msg + ' / '
    if no_lacking > 0:
        msg = msg + str(no_lacking) + ' ' + "\N{HEAVY PLUS SIGN}" 
    logger.info(msg)

# file operations individually (for stdout)
def notice_udeleted(entry):
    msg = ' ' + "\N{WARNING SIGN}" + ' ' + entry['poca_filename'] + \
        ' deleted by user.'
    logger.debug(msg)

def removing(entry):
    msg = ' ' + "\N{CANCELLATION X}" + ' ' + entry['poca_filename'] + \
        ' [' + str(round(entry['poca_mb'])) + ' Mb]'
    logger.debug(msg)

def downloading(entry):
    msg = ' ' + "\N{DOWNWARDS ARROW LEFTWARDS OF UPWARDS ARROW}" + ' ' + \
        entry['poca_filename'] + ' [' + str(round(entry['poca_mb'])) + ' Mb]'
    logger.debug(msg)

def dl_fail(outcome):
    logger.debug('   Download failed. ' + outcome.msg)

def tag_fail(outcome):
    logger.debug('   Tagging failed. ' + outcome.msg)

# file operations summary (for file log)
def summary(title, udeleted, removed, downed, failed):
    '''print summary to log ('warn' is filtered out in stream)'''
    if udeleted:
        logger.warn(title + '. User deleted: ' + ', '.join(udeleted))
    if removed:
        logger.warn(title + '. Removed: ' + ', '.join(removed))
    if downed:
        logger.warn(title + '. Downloaded: ' + ', '.join(downed))
    if failed:
        logger.warn(title + '. Failed: ' + ', '.join(failed))

