# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""String formatting and logging operations"""

import logging


STREAM = logging.getLogger('POCASTREAM')
SUMMARY = logging.getLogger('POCASUMMARY')

# config reporting
def conffatal(msg):
    '''Fatal errors encountered during config read'''
    STREAM.fatal(msg)

def confinfo(msg):
    '''Feedback/suggestions from reading/creating config'''
    STREAM.info(msg)

# subscription error reporting
def subfatal(title, outcome):
    '''Fatal errors encountered processing a specific subscription'''
    err = "\N{Heavy Exclamation Mark Symbol}"
    STREAM.fatal(title + '. ' + err + 'FATAL' + err + ' ' + outcome.msg)

def suberror(title, outcome):
    '''Non-fatal errors encountered processing a specific subscription'''
    err = "\N{Heavy Exclamation Mark Symbol}"
    STREAM.error(title + '. ' + err + 'ERROR' + err + ' ' + outcome.msg)

# report on intentions based on analysis
def plans(title, no_udeleted, no_unwanted, no_lacking):
    '''Summary of files to be downloaded and deleted'''
    msg = title
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
    STREAM.info(msg)

def removing(entry):
    '''One line per entry telling user of episodes being deleted by poca'''
    size = entry['poca_mb']
    size_str = ' [' + str(round(size)) + ' Mb]' if size else ' [Unknown]'
    msg = ' ' + "\N{CANCELLATION X}" + ' ' + entry['poca_filename'] + size_str
    STREAM.info(msg)

def downloading(entry):
    '''One line per entry telling user of episodes being downloaded by poca'''
    size = entry['poca_mb']
    size_str = ' [' + str(round(size)) + ' Mb]' if size else ' [Unknown]'
    msg = ' ' + "\N{DOWNWARDS ARROW LEFTWARDS OF UPWARDS ARROW}" + ' ' + \
        entry['poca_filename'] + size_str
    STREAM.info(msg)

# single entry failures
def dl_fail(outcome):
    '''Subline telling user of single entry download failure'''
    STREAM.info('   Download failed. ' + outcome.msg)

def tag_fail(outcome):
    '''Subline telling user of single entry tagging failure'''
    STREAM.info('   Tagging failed. ' + outcome.msg)

# file operations summary (for file log)
def summary(title, udeleted, removed, downed, failed):
    '''Print summary to log'''
    if udeleted:
        udeleted_files = [x['poca_filename'] for x in udeleted]
        SUMMARY.info(title + '. User deleted: ' + ', '.join(udeleted_files))
    if removed:
        removed_files = [x['poca_filename'] for x in removed]
        SUMMARY.info(title + '. Removed: ' + ', '.join(removed_files))
    if downed:
        downed_files = [x['poca_filename'] for x in downed]
        SUMMARY.info(title + '. Downloaded: ' + ', '.join(downed_files))
    if failed:
        failed_files = [x['poca_filename'] for x in failed]
        SUMMARY.info(title + '. Failed: ' + ', '.join(failed_files))
