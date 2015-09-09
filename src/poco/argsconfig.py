# Copyright 2010, 2011, 2015 Mads Michelsen (reannual@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.

import argparse


def args_config(paths_dic, about):
    '''Returns arguments from a command line argument parser based on argparse'''
    _parser = argparse.ArgumentParser(description=about)

    _parser.add_argument('-q', '--quiet', action='store_true', \
        default=False, help='Quiet mode (useful for cron jobs)')
    _parser.add_argument('-r', '--restart', action='store_true', \
        default=False, help='Deletes all created directories with contents \
        plus log file and starts over')

    errors_group = _parser.add_argument_group(title='error logging')
    errors_group.add_argument('-f', '--errors-file', action='store', \
        nargs='?', const=paths_dic['errors_log'], default=None, \
        help='Specifies a file to use for error logging; \
        if none are assigned the default errors.log in the \
        .poca directory is used.')
    errors_group.add_argument('-m', '--errors-mail', action='store_true', \
        default=False, help='Use the mail account setup in poca.xml to generate \
        email error logging. One email will be sent per error encountered.')

    args_ns = _parser.parse_args()
    return args_ns

