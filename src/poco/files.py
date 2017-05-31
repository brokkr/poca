# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""File operations"""

import os
import sys
import shutil
import signal
import socket
import urllib.request
import urllib.error

from poco.outcome import Outcome


# download
class NoMoreBufferException(Exception):
    '''Custom sub-classed exception used to trigger except in dl function'''
    pass

class TimesUpException(Exception):
    '''Custom sub-classed exception used to trigger except in dl function'''
    pass

def download_block(u, f, block_size):
    '''Download until there's no more to download'''
    buffer = u.read(block_size)
    if not buffer:
        raise NoMoreBufferException("No more to download")
    f.write(buffer)

def handler(signum, frame):
    raise TimesUpException("Download timed out")

def download_file(url, file_path, settings):
    '''Download function with block time outs'''
    try:
        request = urllib.request.Request(url)
        u = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if not settings.useragent:
            return Outcome(False, str(e))
        try:
            fakeheaders = {"User-Agent" : settings.useragent.text}
            request = urllib.request.Request(url, headers=fakeheaders)
            u = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            return Outcome(False, str(e))
    except socket.error as e:
        return Outcome(False, str(e))

    signal.signal(signal.SIGALRM, handler)
    f = open(file_path, "wb")

    block_size = 8192
    while True:
        signal.alarm(90)
        try:
            download_block(u, f, block_size)
        except NoMoreBufferException as e:
            outcome = Outcome(True, str(e))
            f.close()
            break
        except TimesUpException as e:
            outcome = Outcome(False, str(e))
            f.close()
            del_outcome = delete_file(file_path)
            break
        except KeyboardInterrupt:
            f.close()
            del_outcome = delete_file(file_path)
            sys.exit()

    signal.alarm(0)
    signal.signal(signal.SIGALRM, signal.SIG_DFL)

    return outcome

def download_img_file(url, sub_dir, settings):
    '''Download an image file'''
    try:
        u = urllib.request.urlopen(url)
    except urllib.error.URLError:
        return Outcome(False, 'Couldnt get image')
    subtype = u.headers.get_content_subtype()
    u.close()
    mime_dic = {'bmp': '.bmp', 'gif': '.gif', 'png': '.png',
                'jpeg': '.jpg', 'jpg': '.jpg', 'webp': '.webp'}
    extension = mime_dic[subtype] if subtype in mime_dic else None
    if extension is None:
        return Outcome(False, 'Bad image MIME type')
    else:
        file_path = os.path.join(sub_dir, 'cover' + extension)
        return download_file(url, file_path, settings)

def delete_file(file_path):
    '''Deletes a file'''
    try:
        os.remove(file_path)
        return Outcome(True, file_path + ': File was successfully deleted')
    except OSError as e:
        return Outcome(False, file_path + ': ' + str(e))

def delete_sub(conf, title, reset=False):
    '''Delete subscription files (optionally including history)'''
    sub_dir = os.path.join(conf.xml.settings.base_dir.text, title)
    db_file = os.path.join(conf.paths.db_dir, title)
    try:
        shutil.rmtree(sub_dir)
    except FileNotFoundError:
        pass
    if reset:
        try:
            os.remove(db_file)
        except FileNotFoundError:
            pass

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
    except OSError:
        return Outcome(False, check_dir + ': Dir could not be created.')

def verify_file(entry):
    '''Check to see if recorded file exists or has been removed'''
    isfile = os.path.isfile(entry['poca_abspath'])
    return Outcome(isfile, entry['poca_abspath'] + ' exists: ' + str(isfile))
