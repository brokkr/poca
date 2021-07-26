# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""File operations"""

import os
import shutil
import requests

from threading import current_thread
from pathlib import Path

from poca.outcome import Outcome


def download_file(entry, dl_settings):
    '''Download function with block time outs'''
    my_thread = current_thread()
    headers = requests.utils.default_headers()
    url = entry['poca_url']
    if dl_settings['useragent']:
        headers.update({'User-Agent': dl_settings['useragent']})
    if getattr(my_thread, "kill", False):
        return Outcome(None, 'Download cancelled by user')
    try:
        r = requests.get(url, stream=True, timeout=60, headers=headers)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError) as e:
        return Outcome(False, 'Download of %s failed' % url)
    except requests.exceptions.Timeout:
        return Outcome(False, 'Download of %s timed out' % url)
    if r.status_code >= 400:
        return Outcome(False, 'Download of %s failed' % url)
    filename_keys = ['permissive', 'ntfs', 'restrictive', 'fallback']
    start_at = dl_settings.get('filenames', 'permissive')
    if start_at in filename_keys:
        filename_keys = filename_keys[filename_keys.index(start_at):]
    if not entry['unique_filename']:
        filename_keys = ['fallback']
    for key in filename_keys:
        filename = '.'.join((entry['names'][key], entry['extension']))
        file_path = entry['directory'].joinpath(filename)
        try:
            with file_path.open(mode='wb') as f:
                try:
                    for chunk in r.iter_content(chunk_size=1024):
                        if getattr(my_thread, "kill", False):
                            r.close()
                            _outcome = delete_file(f.name)
                            return Outcome(None, 'Download cancelled by user')
                        if chunk:
                            f.write(chunk)
                    r.close()
                    return Outcome(True, (filename, file_path))
                except requests.exceptions.ConnectionError as e:
                    r.close()
                    _outcome = delete_file(f.name)
                    return Outcome(False, 'Download of %s broke off' % url)
                except requests.exceptions.Timeout:
                    r.close()
                    _outcome = delete_file(f.name)
                    return Outcome(False, 'Download of %s timed out' % url)
        except OSError:
            #print('%s did not work, trying another...' % file_path)
            pass
            # testing
    # this should really never happen
    return Outcome(False, 'Somehow none of the filenames we tried worked')

def download_img_file(url, sub_dir):
    '''Download an image file'''
    try:
        r = requests.get(url, timeout=60)
    except requests.exceptions.RequestException:
        return Outcome(False, 'Download of %s failed' % url)
    content_type = r.headers['content-type'].lower()
    mime_dic = {'image/bmp': '.bmp',
                'image/gif': '.gif',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp'}
    extension = mime_dic.get(content_type, None)
    # maybe tell user content_type (helps with debugging)
    if extension is None:
        return Outcome(False, 'Download of image failed. Unknown MIME type.')
    filename = ''.join(('cover', extension))
    file_path = sub_dir.joinpath(filename)
    if file_path.is_file():
        file_size = str(file_path.stat().st_size)
        remote_size = r.headers.get('content-length', str(len(r.content)))
        if file_size == remote_size:
            return Outcome(True, 'Same image file already downloaded')
    with file_path.open(mode='wb') as f:
        f.write(r.content)
    return Outcome(True, 'Image file downloaded')

def delete_file(it):
    '''Deletes a file'''
    file_path = Path(it.path)
    try:
        os.remove(file_path)
        return Outcome(True, file_path + ': File was successfully deleted')
    except OSError as e:
        return Outcome(False, 'Could not delete %s' % file_path)


def verify_file(entry):
    '''Check to see if recorded file exists or has been removed'''
    isfile = os.path.isfile(entry['poca_abspath'])
    return Outcome(isfile, entry['poca_abspath'] + ' exists: ' + str(isfile))


def check_path(check_dir):
    '''Check directory exists and is writable; if not create directory'''
    if check_dir.is_dir():
        if os.access(check_dir, os.W_OK):
            return Outcome(True, '%s exists already' % check_dir.absolute())
        else:
            return Outcome(False, 'Could not save files to %s' % \
                           check_dir.absolute())
    try:
        os.makedirs(check_dir.absolute())
        return Outcome(True, '%s was created' % check_dir.absolute())
    except FileExistsError:
        return Outcome(False, 'Could not create %s. File already exists?' \
                       % check_dir.absolute())
    except (OSError, PermissionError) as e:
        return Outcome(False, 'Could not create %s.'  % check_dir.absolute())

def check_file_write(check_file):
    '''Check to see if file is writable/can be created'''
    if check_file.is_file():
        if os.access(check_file, os.W_OK):
            return Outcome(True, '%s exists and is writable' % \
                           check_file.absolute())
        else:
            return Outcome(False, '%s exists but is not writable' % \
                           check_file.absolute())
    if check_file.is_dir():
        return Outcome(False, '%s is a directory, not a file' % \
                       check_file.absolute())
    outcome = check_path(check_file.parent)
    return outcome

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
