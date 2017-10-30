# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""String formatting and logging operations"""

import logging


STREAM = logging.getLogger('POCA_STREAM')
AFTER_STREAM = logging.getLogger('POCA_AFTER_STREAM')
SUMMARY = logging.getLogger('POCA_SUMMARY')


# ####################################### #
# SUBSCRIBE                               #
# ####################################### #

def geninfo(msg):
    '''Generic info'''
    STREAM.info(msg)

def generror(msg):
    '''Generic error'''
    err = "\N{Heavy Exclamation Mark Symbol}"
    msg = err + 'ERROR' + err + ' ' + msg
    STREAM.error(msg)


# ####################################### #
# GLOBAL                                  #
# ####################################### #

def config_fatal(msg):
    '''Fatal errors encountered during config read'''
    STREAM.fatal(msg)


# ####################################### #
# PLANNING                                #
# ####################################### #

def plans_error(subdata):
    '''sub-fatal errors encountered processing a specific subscription'''
    stream_msg = "%s. %s" % (subdata.sub.title.text.upper(), subdata.outcome.msg)
    after_stream_msg = 'SUB ERROR: %s' % (subdata.outcome.msg)
    STREAM.debug(stream_msg)
    AFTER_STREAM.info(after_stream_msg)
    SUMMARY.error(stream_msg)

def plans_moved(subdata, _outcome):
    '''Sub has moved (http status 301)'''
    stream_msg = "%s. %s" % (subdata.sub.title.text.upper(), _outcome.msg)
    after_stream_msg = 'SUB MOVED: %s' % (_outcome.msg)
    STREAM.debug(stream_msg)
    AFTER_STREAM.info(after_stream_msg)
    SUMMARY.error(stream_msg)

def plans_nochanges(subdata):
    '''No changes made, just output title'''
    msg = subdata.sub.title.text.upper()
    STREAM.info(msg)

def plans_upgrade(subdata):
    '''Summary of files to be downloaded and deleted'''
    msg = subdata.sub.title.text.upper()
    no_udeleted = len(subdata.udeleted)
    no_unwanted = len(subdata.unwanted)
    no_lacking = len(subdata.lacking)
    if no_udeleted > 0 or no_unwanted > 0 or no_lacking > 0:
        msg = msg + '. '
    if no_udeleted > 0:
        msg = msg + str(no_udeleted) + ' ' + "\N{CIRCLE WITH SUPERIMPOSED X}"
    if no_udeleted > 0 and (no_unwanted > 0 or no_lacking > 0):
        msg = msg + ' / '
    if no_unwanted > 0:
        msg = msg + str(no_unwanted) + ' ' + "\N{HEAVY MINUS SIGN}"
    if no_unwanted > 0 and no_lacking > 0:
        msg = msg + ' / '
    if no_lacking > 0:
        msg = msg + str(no_lacking) + ' ' + "\N{HEAVY PLUS SIGN}"
    STREAM.info(msg)


# ####################################### #
# PROCESSING                              #
# ####################################### #

def processing_user_deleted(entry):
    '''One line per entry telling user of episodes deleted by user'''
    msg = ' ' + "\N{CIRCLE WITH SUPERIMPOSED X}" + ' ' + entry['poca_filename'] + \
        ' deleted by user'
    STREAM.debug(msg)

def processing_removal(entry):
    '''One line per entry telling user of episodes being deleted by poca'''
    size = entry['poca_mb']
    size_str = ' [' + str(round(size)) + ' Mb]' if size else ' [Unknown]'
    msg = ' ' + "\N{CANCELLATION X}" + ' ' + entry['poca_filename'] + size_str
    STREAM.debug(msg)

def processing_download(entry):
    '''One line per entry telling user of episodes being downloaded by poca'''
    size = entry['poca_mb']
    size_str = ' [' + str(round(size)) + ' Mb]' if size else ' [Unknown]'
    msg = ' ' + "\N{DOWNWARDS ARROW LEFTWARDS OF UPWARDS ARROW}" + ' ' + \
        entry['poca_filename'] + size_str
    STREAM.debug(msg)


# ####################################### #
# FAIL                                    #
# ####################################### #

def fail_common(msg, after_stream_msg):
    stream_msg = ' \N{WARNING SIGN} ' + msg
    STREAM.debug(stream_msg)
    AFTER_STREAM.info(after_stream_msg)

def fail_download(outcome):
    '''Subline telling user of single entry download failure'''
    after_stream_msg = 'DOWNLOAD ERROR: %s' % (outcome.msg)
    fail_common(outcome.msg, after_stream_msg)

def fail_tag(outcome):
    '''Subline telling user of single entry tagging failure'''
    after_stream_msg = 'TAGGING ERROR: %s' % (outcome.msg)
    fail_common(outcome.msg, after_stream_msg)

def fail_delete(outcome):
    '''Subline telling user of single entry deletion failure'''
    after_stream_msg = 'DELETE ERROR: %s' % (outcome.msg)
    fail_common(outcome.msg, after_stream_msg)

def fail_database(outcome):
    '''Subline telling user of failure to save jar'''
    after_stream_msg = 'DATABASE ERROR: %s' % (outcome.msg)
    fail_common(outcome.msg, after_stream_msg)

def after_stream_flush():
    '''Outputs all buffered failures in one go. In verbose mode after_stream
       is not enabled.'''
    if AFTER_STREAM.poca_memory_handler:
        if AFTER_STREAM.poca_memory_handler.buffer:
            STREAM.info('The following issues were encountered: ')
            AFTER_STREAM.poca_memory_handler.flush()
            AFTER_STREAM.poca_memory_handler.close()


# ####################################### #
# SUMMARY                                 #
# ####################################### #

# file operations summary (for file log)
def file_summary(subdata, removed, downed, failed):
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

def email_summary():
    '''Empty out buffered email logs (if needed)'''
    if SUMMARY.poca_email_handler:
        SUMMARY.poca_email_handler.close()
        outcome = SUMMARY.poca_email_handler.outcome
        if outcome.success is False:
            config_fatal('Email log failed with: ')
            config_fatal('  ' + outcome.msg)
