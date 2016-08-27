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
    logger.fatal(title + '( fatal ) ' + outcome.msg)

def suberror(title, outcome):
    logger.error(title + '( error ) ' + outcome.msg)

# report on intentions based on analysis
def plans(title, no_unwanted, no_lacking):
    msg = title
    if no_unwanted > 0:
        msg = msg + str(no_unwanted) + ' file(s) to be removed. ' 
    if no_lacking > 0:
        msg = msg + str(no_lacking) + ' file(s) to be downloaded.'
    if no_unwanted == 0 and no_lacking == 0:
        msg = msg + 'No changes.'
    logger.info(msg)

# file operations individually (for stdout)
def removing(entry):
    logger.debug('  -  ' + entry['poca_filename'] + 
        '  [ ' + str(entry['poca_mb']) + ' Mb ] ...')

def downloading(entry):
    logger.debug('  +  ' + entry['poca_filename'] + 
        '  [ ' + str(entry['poca_mb']) + ' Mb ] ...')

def dl_fail(outcome):
    logger.debug('     Download failed. ' + outcome.msg)

def tag_fail(outcome):
    logger.debug('     Tagging failed. ' + outcome.msg)

# file operations summary (for file log)
def summary(title, downed, removed, failed):
    '''print summary to log ('warn' is filtered out in stream)'''
    if downed:
        logger.warn(title + 'Downloaded: ' + ', '.join(downed))
    if failed:
        logger.warn(title + 'Failed: ' + ', '.join(failed))
    if removed:
        logger.warn(title + 'Removed: ' + ', '.join(removed))

