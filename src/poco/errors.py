# Copyright 2010, 2011, 2015 Mads Michelsen (reannual@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.


import logging
import sys
import socket


def errors(error_msg, suggest_msg, fatal=False, title=''):
    stream_logger = logging.getLogger('slogger')
    remote_logger = logging.getLogger('rlogger')
    logging.raiseExceptions = 0
    stream_logger.error(error_msg)
    remote_logger.error(title + error_msg + ' '.join(suggest_msg))
    if fatal:
        sys.exit()


