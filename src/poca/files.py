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

from threading import current_thread

from poca.outcome import Outcome


def download_file(url, file_path, settings):
    '''Download function with block time outs'''
    my_thread = current_thread()
    headers = requests.utils.default_headers()
    if settings.useragent.text:
        useragent = {'User-Agent': settings.useragent.text}
        headers.update(useragent)
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
    with open(file_path, 'wb') as f:
        try:
            for chunk in r.iter_content(chunk_size=1024):
                if getattr(my_thread, "kill", False):
                    r.close()
                    _outcome = delete_file(f.name)
                    return Outcome(None, 'Download cancelled by user')
                if chunk:
                    f.write(chunk)
        except requests.exceptions.ConnectionError as e:
            r.close()
            _outcome = delete_file(f.name)
            return Outcome(False, 'Download of %s broke off' % url)
        except requests.exceptions.Timeout:
            r.close()
            _outcome = delete_file(f.name)
            return Outcome(False, 'Download of %s timed out' % url)
    r.close()
    return Outcome(True, '')


def download_img_file(url, sub_dir, settings):
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
    if extension is None:
        return Outcome(False, 'Download of image %s failed. Unknown MIME type.'
                       % url)
    else:
        file_path = os.path.join(sub_dir, 'cover' + extension)
        with open(file_path, 'wb') as f:
            f.write(r.content)
    return Outcome(True, '')


def delete_file(file_path):
    '''Deletes a file'''
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
    '''Create a directory'''
    if os.path.isdir(check_dir):
        if os.access(check_dir, os.W_OK):
            return Outcome(True, '%s exists already' % check_dir)
        else:
            return Outcome(False, 'Could not save files to %s' % check_dir)
    try:
        os.makedirs(check_dir)
        return Outcome(True, '%s was successfully created' % check_dir)
    except OSError:
        return Outcome(False, 'Could not create %s' % check_dir)


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
