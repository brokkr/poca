# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""String formatting and logging operations"""

import logging


STREAM = logging.getLogger('POCASTREAM')
STREAMFAIL = logging.getLogger('POCASTREAMFAIL')
SUMMARY = logging.getLogger('POCASUMMARY')

# generic output
def geninfo(msg):
    '''Generic info'''
    STREAM.info(msg)

def generror(msg):
    '''Generic error'''
    err = "\N{Heavy Exclamation Mark Symbol}"
    msg = err + 'ERROR' + err + ' ' + msg
    STREAM.error(msg)

# config reporting
def conffatal(msg):
    '''Fatal errors encountered during config read'''
    STREAM.fatal(msg)

# subscription plans and error reporting
def suberror(subdata):
    '''Non-fatal errors encountered processing a specific subscription'''
    msg = "%s. %s" % (subdata.sub.title.text.upper(), subdata.outcome.msg)
    STREAM.error(msg)
    SUMMARY.error(msg)

def subplans(subdata):
    '''Summary of files to be downloaded and deleted'''
    msg = subdata.sub.title.text.upper()
    no_udeleted = len(subdata.udeleted)
    no_unwanted = len(subdata.unwanted)
    no_lacking = len(subdata.lacking)
    if no_udeleted > 0 or no_unwanted > 0 or no_lacking > 0:
        msg = msg + '. '
    if no_udeleted > 0:
        msg = msg + str(no_udeleted) + ' ' + "\N{WARNING SIGN}"
    if no_udeleted > 0 and (no_unwanted > 0 or no_lacking > 0):
        msg = msg + ' / '
    if no_unwanted > 0:
        msg = msg + str(no_unwanted) + ' ' + "\N{HEAVY MINUS SIGN}"
    if no_unwanted > 0 and no_lacking > 0:
        msg = msg + ' / '
    if no_lacking > 0:
        msg = msg + str(no_lacking) + ' ' + "\N{HEAVY PLUS SIGN}"
    STREAM.info(msg)

# file operations individually (for stdout)
def notice_udeleted(entry):
    '''One line per entry telling user of episodes deleted by user'''
    msg = ' ' + "\N{WARNING SIGN}" + ' ' + entry['poca_filename'] + \
        ' deleted by user'
    STREAM.debug(msg)

def removing(entry):
    '''One line per entry telling user of episodes being deleted by poca'''
    size = entry['poca_mb']
    size_str = ' [' + str(round(size)) + ' Mb]' if size else ' [Unknown]'
    msg = ' ' + "\N{CANCELLATION X}" + ' ' + entry['poca_filename'] + size_str
    STREAM.debug(msg)
    STREAMFAIL.info(msg)

def downloading(entry):
    '''One line per entry telling user of episodes being downloaded by poca'''
    size = entry['poca_mb']
    size_str = ' [' + str(round(size)) + ' Mb]' if size else ' [Unknown]'
    msg = ' ' + "\N{DOWNWARDS ARROW LEFTWARDS OF UPWARDS ARROW}" + ' ' + \
        entry['poca_filename'] + size_str
    STREAM.debug(msg)

# file operations failures
def dl_fail(outcome):
    '''Subline telling user of single entry download failure'''
    STREAM.debug('   ' + outcome.msg)

def tag_fail(outcome):
    '''Subline telling user of single entry tagging failure'''
    STREAM.debug('   Tagging failed. ' + outcome.msg)

def del_fail(outcome):
    '''Subline telling user of single entry deletion failure'''
    STREAM.debug('   Deletion failed. ' + outcome.msg)

# file operations summary (for file log)
def summary(subdata, removed, downed, failed):
    '''Print summary to log'''
    title = subdata.sub.title.text.upper()
    if subdata.udeleted:
        udeleted_files = [x['poca_filename'] for x in subdata.udeleted]
        SUMMARY.info(title + '. User deleted: ' + ', '.join(udeleted_files))
    if removed:
        removed_files = [x['poca_filename'] for x in removed]
        SUMMARY.info(title + '. Removed: ' + ', '.join(removed_files))
    if downed:
        downed_files = [x['poca_filename'] for x in downed]
        SUMMARY.info(title + '. Downloaded: ' + ', '.join(downed_files))
    if failed:
        failed_files = [x['poca_filename'] for x in failed]
        SUMMARY.error(title + '. Failed: ' + ', '.join(failed_files))
