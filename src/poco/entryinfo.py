# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Get more information on a single feed entry"""

import time
from os import path
import urllib.request, urllib.error, urllib.parse


def validate(entry):
    '''Validates entry if it contains an enclosure'''
    try:
        entry['poca_url'] = entry.enclosures[0]['href']
        entry['valid'] = True
    except (KeyError, IndexError, AttributeError):
        entry['valid'] = False
        return entry
    parsed_url = urllib.parse.urlparse(entry['poca_url'])
    parsed_path = urllib.parse.unquote(parsed_url.path)
    entry['poca_filename'] = path.basename(parsed_path)
    return entry


def expand(entry, sub, sub_dir):
    '''Expands entry with url, paths and size'''
    try:
        entry['poca_size'] = int(entry.enclosures[0]['length'])
        if entry['poca_size'] == 0:
            raise ValueError
        entry['poca_mb'] = round(entry.poca_size / 1048576.0, 2)
    except (KeyError, ValueError, TypeError):
        entry['poca_size'] = None
        entry['poca_mb'] = None
    entry['poca_basename'], _ext = path.splitext(entry['poca_filename'])
    entry['poca_ext'] = _ext[1:]
    if hasattr(sub, 'rename'):
        entry = rename(entry, sub)
    entry['poca_filename'] = '.'.join((entry['poca_basename'],
                                      entry['poca_ext']))
    entry['poca_abspath'] = path.join(sub_dir, entry['poca_filename'])
    print(entry['poca_abspath'])
    entry['valid'] = True
    return entry


def rename(entry, sub):
    element_lst = [el for el in sub.rename.iterchildren()]
    rename_lst = []
    for el in element_lst:
        if el.tag == 'published_parsed':
            _str = time.strftime('%Y-%m-%d', entry['published_parsed'])
        elif el.tag == 'title':
            _str = sub.title.text
        rename_lst.append(_str)
    divider = sub.rename.get('divider') or '_'
    if rename_lst:
        entry['poca_basename'] = divider.join(rename_lst)
    print(entry['poca_basename'])
    return entry
