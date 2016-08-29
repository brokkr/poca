# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# except download function copyright PabloG 
# (http://stackoverflow.com/users/394/pablog) and Mads Michelsen 2015, 2016
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import os
import signal
import socket
import urllib.request
import urllib.error

from poco.outcome import Outcome


# download
class NoMoreBufferException(Exception):
    pass

class TimesUpException(Exception):
    pass

def download_block(u, f, block_size):
    buffer = u.read(block_size)
    if not buffer:
        raise NoMoreBufferException("No more to download")
    f.write(buffer)

def handler(signum, frame):
    raise TimesUpException("Download timed out")

def download_audio_file(entry):
    '''Download function with block time outs'''
    signal.signal(signal.SIGALRM, handler)

    try:
        u = urllib.request.urlopen(entry['poca_url'])
    except urllib.error.HTTPError as e:
        return Outcome(False, "HTTPError: " + str(e))
    except:
        return Outcome(False, "Unknown error")
    f = open(entry['poca_abspath'], "wb")

    block_size = 8192
    while True:
        # "Any previously scheduled alarm is canceled 
        # (only one alarm can be scheduled at any time)"
        signal.alarm(5)
        try:
            download_block(u, f, block_size)
        except NoMoreBufferException as e:
            outcome = Outcome(True, str(e))
            break
        except TimesUpException as e:
            outcome = Outcome(False, str(e))
            break

    signal.signal(signal.SIGALRM, signal.SIG_DFL)

    f.close()
    return outcome

# delete
def delete_file(file_path):
    '''Deletes a file'''
    # standardise on the dataunit being passed around?
    # this should be a entry not a filename
    try:
        os.remove(file_path)
        return Outcome(True, file_path + ': File was successfully deleted')
    except OSError as e:
        return Outcome(False, file_path + ': ' + str(e))

# permissions check
def check_path(check_dir):
    '''Create a directory'''
    if os.path.isdir(check_dir):
        if os.access(check_dir, os.W_OK):
            return Outcome(True, check_dir + ': Dir exists already.')
        else:
            return Outcome(False, check_dir + ': Lacks permissions to dir.')
    try:
        os.makedirs(check_dir)
        return Outcome(True, check_dir + ': Dir was successfully created.')
    except OSError as e:
        return Outcome(False, check_dir + ': Dir could not be created.')

