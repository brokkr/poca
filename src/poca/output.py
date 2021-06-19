# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""String formatting and logging operations"""


import sys
import logging


STREAM = logging.getLogger('POCA_STREAM')
AFTER_STREAM = logging.getLogger('POCA_AFTER_STREAM')
SUMMARY = logging.getLogger('POCA_SUMMARY')

ERROR_DIC = {'default': '\u203c', 'ascii': '!', 'wsl': '\u203c', \
             'emoji': '\U0001f6a8'}
AUTODEL_DIC = {'default': '\u2717', 'ascii': 'X', 'wsl': '\u2717', \
               'emoji': '\U0001f5d1\ufe0f'}
USERDEL_DIC = {'default': '\u2718', 'ascii': '%', 'wsl': '\u2718', \
               'emoji': '\U0001f6ae'}
PLANADD_DIC = {'default': '\u2795', 'ascii': '+', 'wsl': '+', \
               'emoji': '\U0001f44d'}
PLANREM_DIC = {'default': '\u2796', 'ascii': '-', 'wsl': '-', \
               'emoji': '\U0001f44e'}
DOWNLOAD_DIC = {'default': '\u21af', 'ascii': '>', 'wsl': '\u21af', \
                'emoji': '\U0001f4be'}


# ####################################### #
# SUBSCRIBE                               #
# ####################################### #

def subscribe_info(msg):
    '''Generic info'''
    STREAM.info(msg)


def subscribe_error(msg):
    '''Generic error'''
    ERROR = ERROR_DIC[STREAM.glyphs]
    err = ' %s ' % ERROR
    msg = err + msg
    STREAM.error(msg)


# ####################################### #
# GLOBAL                                  #
# ####################################### #

def config_fatal(msg):
    '''Fatal errors encountered during config read'''
    ERROR = ERROR_DIC[STREAM.glyphs]
    STREAM.fatal(' %s %s' % (ERROR, msg))
    sys.exit(1)


# ####################################### #
# PLANNING                                #
# ####################################### #

def plans_error(subdata):
    '''sub-fatal errors encountered processing a specific subscription'''
    stream_msg = '%s. %s' % (subdata.sub.title.text.upper(),
                             subdata.outcome.msg)
    after_stream_msg = 'SUB ERROR (%s): %s' % (subdata.sub.title.text,
                                               subdata.outcome.msg)
    STREAM.debug(stream_msg)
    AFTER_STREAM.info(after_stream_msg)
    SUMMARY.error(stream_msg)


def plans_moved(subdata, _outcome):
    '''Sub has moved (http status 301) - succes/failure in updating config'''
    stream_msg = '%s. %s' % (subdata.sub.title.text.upper(), _outcome.msg)
    after_stream_msg = 'SUB MOVE (301) (%s): %s' % (subdata.sub.title.text,
                                                    _outcome.msg)
    STREAM.debug(stream_msg)
    AFTER_STREAM.info(after_stream_msg)
    SUMMARY.error(stream_msg)


def plans_nochanges(subdata):
    '''No changes made, just output title'''
    msg = subdata.sub.title.text.upper()
    STREAM.info(msg)


def plans_upgrade(subdata):
    '''Summary of files to be downloaded and deleted'''
    USERDEL = USERDEL_DIC[STREAM.glyphs]
    PLANADD = PLANADD_DIC[STREAM.glyphs]
    PLANREM = PLANREM_DIC[STREAM.glyphs]
    msg = subdata.sub.title.text.upper()
    no_udeleted = len(subdata.udeleted)
    no_unwanted = len(subdata.unwanted)
    no_lacking = len(subdata.lacking)
    if no_udeleted > 0 or no_unwanted > 0 or no_lacking > 0:
        msg = msg + '. '
    if no_udeleted > 0:
        msg = msg + str(no_udeleted) + ' ' + USERDEL
    if no_udeleted > 0 and (no_unwanted > 0 or no_lacking > 0):
        msg = msg + ' / '
    if no_unwanted > 0:
        msg = msg + str(no_unwanted) + ' ' + PLANREM
    if no_unwanted > 0 and no_lacking > 0:
        msg = msg + ' / '
    if no_lacking > 0:
        msg = msg + str(no_lacking) + ' ' + PLANADD
    STREAM.info(msg)


# ####################################### #
# PROCESSING                              #
# ####################################### #

def processing_user_deleted(entry):
    USERDEL = USERDEL_DIC[STREAM.glyphs]
    '''One line per entry telling user of episodes deleted by user'''
    episode = entry['title'] or entry['poca_filename']
    msg = ' %s %s deleted by user' % (USERDEL, episode)
    STREAM.debug(msg)


def processing_removal(entry):
    '''One line per entry telling user of episodes being deleted by poca'''
    AUTODEL = AUTODEL_DIC[STREAM.glyphs]
    episode = entry['title'] or entry['poca_filename']
    size = entry['poca_mb']
    size_str = ' [%s Mb]' % str(round(size)) if size else ' [Unknown]'
    msg = ' %s %s %s' % (AUTODEL, episode, size_str)
    STREAM.debug(msg)


def processing_download(entry):
    '''One line per entry telling user of episodes being downloaded by poca'''
    DOWNLOAD = DOWNLOAD_DIC[STREAM.glyphs]
    episode = entry['title'] or entry['poca_filename']
    size = entry['poca_mb']
    size_str = ' [%s Mb]' % str(round(size)) if size else ' [Unknown]'
    msg = ' %s %s %s' % (DOWNLOAD, episode, size_str)
    STREAM.debug(msg)


# ####################################### #
# FAIL                                    #
# ####################################### #

def fail_common(msg, after_stream_msg):
    ERROR = ERROR_DIC[STREAM.glyphs]
    stream_msg = ' %s %s' % (ERROR, msg)
    STREAM.debug(stream_msg)
    AFTER_STREAM.info(after_stream_msg)


def fail_download(title, outcome):
    '''Subline telling user of single entry download failure'''
    after_stream_msg = 'DOWNLOAD ERROR (%s): %s' % (title, outcome.msg)
    fail_common(outcome.msg, after_stream_msg)


def fail_tag(title, outcome):
    '''Subline telling user of single entry tagging failure'''
    after_stream_msg = 'TAGGING ERROR (%s): %s' % (title, outcome.msg)
    fail_common(outcome.msg, after_stream_msg)


def fail_delete(title, outcome):
    '''Subline telling user of single entry deletion failure'''
    after_stream_msg = 'DELETE ERROR (%s): %s' % (title, outcome.msg)
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
        udeleted_files = [x['filename'] for x in subdata.udeleted]
        SUMMARY.info(title + '. User deleted: ' + ', '.join(udeleted_files))
    if removed:
        removed_files = [x['filename'] for x in removed]
        SUMMARY.info(title + '. Removed: ' + ', '.join(removed_files))
    if downed:
        downed_files = [x['filename'] for x in downed]
        SUMMARY.info(title + '. Downloaded: ' + ', '.join(downed_files))
    if failed:
        failed_files = [x['title'] for x in failed]
        SUMMARY.error(title + '. Failed: ' + ', '.join(failed_files))


def email_summary():
    '''Empty out buffered email logs (if needed)'''
    if SUMMARY.poca_email_handler:
        SUMMARY.poca_email_handler.close()
        outcome = SUMMARY.poca_email_handler.outcome
        if outcome.success is False:
            config_fatal('Email log failed with: %s' % outcome.msg)
