# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.


import logging
import logging.handlers


category_synonyms = [ \
    ('red', 'Known and retired', 'reset'), \
    ('yellow', 'Known and in use', 'reset'), \
    ('green', 'Heretofore unknown', 'reset'), \
    ('oranges', 'All known', 'reset'), \
    ('lemons', 'All potential', 'reset'), \
    ('limes', 'To be used', 'reset'), \
    ('pomelos', 'To be downloaded', 'green'), \
    ('grapefruits', 'To be deleted', 'red'), \
    ('citrons', 'To be discarded', 'reset') \
    ]

color_codes = { \
    'reset': '\033[0;0m', \
    'bold': '\033[1m', \
    'red': '\033[31m', \
    'green': '\033[32m', \
    'blue': '\033[34m', \
    'lred': '\033[1;31m', \
    'lgreen': '\033[1;32m', \
    'yellow': '\033[1;33m', \
    'lblue': '\033[1;34m' \
    }

def _colorize(_string, color):
    return color_codes[color] + str(_string) + color_codes['reset']

def loggers(args_ns):
    stream_logger = logging.getLogger('slogger')
    stream_logger.setLevel(logging.WARN)
    remote_logger = logging.getLogger('rlogger')
    remote_logger.setLevel(logging.WARN)

    null_handler = logging.NullHandler()
    null_handler.setLevel(logging.WARN)
    stream_logger.addHandler(null_handler)
    remote_logger.addHandler(null_handler)

    if not args_ns.quiet:
        stream_formatter = logging.Formatter(_colorize("Error: ", 'lred') + \
        "%(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.ERROR)
        stream_handler.setFormatter(stream_formatter)
        stream_logger.addHandler(stream_handler)
    if args_ns.errors_file:
        file_formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler = logging.FileHandler(args_ns.errors_file)
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(file_formatter)
        remote_logger.addHandler(file_handler)
    return (stream_logger, remote_logger)

def add_mail_handler(sets_dic, remote_logger):
    mail_formatter = logging.Formatter("%(asctime)s - %(message)s")
    mail_handler = logging.handlers.SMTPHandler(sets_dic['mail_account']['host'], \
    sets_dic['mail_account']['fromaddr'], \
    [sets_dic['mail_account']['toaddr']], \
    sets_dic['mail_account']['subject'])
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(mail_formatter)
    remote_logger.addHandler(mail_handler)
    return remote_logger

def print_heading(args_ns, sub_dic, i):
    '''Prints heading for each channel'''
    if not args_ns.quiet:
        if i > 0: print
        print _colorize(' '.join(sub_dic['title'].upper()), 'bold')

def print_no_news_is_good_news(args_ns):
    '''Informs user that no new entries were found in a subscription'''
    if not args_ns.quiet:
        print 'No new entries found'

def print_stats(args_ns, sub_dic, entries):
    '''Prints the categories and their number'''
    if args_ns.quiet:
        return
    for i, category in enumerate(category_synonyms):
        if i in [3,4,5,8]: continue
        no_items = len(entries[category[0]])
        print category[1].ljust(21), _colorize(no_items, category[2])


