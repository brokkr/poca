# -*- coding: utf-8 -*-


# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""File operations"""

import os
import shutil
import requests

from poco.outcome import Outcome

# download functions
def download_file(url, file_path, settings, run_event):
    '''Download function with block time outs'''
    try:
        r = requests.get(url, stream=True, timeout=60)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError) as e:
        r.close()
        return Outcome(False, 'Download failed: %s' % str(e))
    except requests.exceptions.Timeout:
        r.close()
        return Outcome(False, 'Download timed out')
    with open(file_path, 'wb') as f:
        try:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                if not run_event.is_set():
                    r.close()
                    os.remove(f.name)
                    print(file_path, "download stopped")
                    return Outcome(False, 'Download stopped')
        except requests.exceptions.ConnectionError as e:
            r.close()
            os.remove(f.name)
            return Outcome(False, 'Download broke off: %s' % str(e))
        except requests.exceptions.Timeout:
            r.close()
            os.remove(f.name)
            return Outcome(False, 'Download timed out')
    r.close()
    return Outcome(True, '')

def download_img_file(url, sub_dir, settings):
    '''Download an image file'''
    try:
        r = requests.get(url, timeout=60)
    except requests.exceptions.RequestException:
        return Outcome(False, 'Download failed')
    content_type = r.headers['content-type']
    mime_dic = {'image/bmp': '.bmp',
                'image/gif': '.gif',
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp'}
    extension = mime_dic.get(content_type, None)
    if extension is None:
        return Outcome(False, 'Unknown image MIME type')
    else:
        file_path = os.path.join(sub_dir, 'cover' + extension)
        with open(file_path, 'wb') as f:
            f.write(r.content)
    return Outcome(True, '')

# single file functions
def delete_file(file_path):
    '''Deletes a file'''
    try:
        os.remove(file_path)
        return Outcome(True, file_path + ': File was successfully deleted')
    except OSError as e:
        return Outcome(False, file_path + ': ' + str(e))

def verify_file(entry):
    '''Check to see if recorded file exists or has been removed'''
    isfile = os.path.isfile(entry['poca_abspath'])
    return Outcome(isfile, entry['poca_abspath'] + ' exists: ' + str(isfile))

# directory functions
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


# subscription reset
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
