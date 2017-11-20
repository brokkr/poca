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
import urllib.request
import urllib.error
import urllib.parse


def validate(entry):
    '''Validates entry if it contains an enclosure'''
    entry['expanded'] = False
    try:
        entry['poca_url'] = entry.enclosures[0]['href']
        entry['valid'] = True
    except (KeyError, IndexError, AttributeError):
        entry['valid'] = False
        return entry
    parsed_url = urllib.parse.urlparse(entry['poca_url'])
    parsed_path = urllib.parse.unquote(parsed_url.path)
    entry['filename'] = path.basename(parsed_path)
    return entry


def expand(entry, sub, sub_dir):
    '''Expands entry with url, paths and size'''
    if entry['expanded'] is True:
        return entry
    try:
        entry['poca_size'] = int(entry.enclosures[0]['length'])
        if entry['poca_size'] == 0:
            raise ValueError
        entry['poca_mb'] = round(entry.poca_size / 1048576.0, 2)
    except (KeyError, ValueError, TypeError):
        entry['poca_size'] = None
        entry['poca_mb'] = None
    entry['poca_basename'], _ext = path.splitext(entry['filename'])
    entry['poca_ext'] = _ext[1:]
    if hasattr(sub, 'rename'):
        entry = rename(entry, sub)
    entry['poca_filename'] = '.'.join((entry['poca_basename'],
                                      entry['poca_ext']))
    entry['poca_abspath'] = path.join(sub_dir, entry['poca_filename'])
    entry['expanded'] = True
    return entry


def rename(entry, sub):
    forbidden = ['/', '\\', ':', '\'', '\"', ',', ';', '.']
    try:
        date = time.strftime('%Y-%m-%d', entry['published_parsed'])
    except (KeyError, TypeError):
        date = 'missing_pub_date'
    uid = str(entry['id']) if 'id' in entry else 'missing_uid'
    uid = ''.join([x for x in uid if x not in forbidden])
    episode_title = str(entry['title']) if 'title' in entry else \
        'missing_title'
    rename_dic = {'org_name': entry['poca_basename'],
                  'title': sub.title.text,
                  'episode_title': episode_title,
                  'uid': uid,
                  'date': date}
    rename_lst = [rename_dic[el.tag] for el in sub.rename.iterchildren() if
                  el.tag in rename_dic]
    divider = sub.rename.get('divider') or ' '
    space = sub.rename.get('space') or ' '
    if rename_lst:
        basename = divider.join(rename_lst).replace(' ', space)
        entry['poca_basename'] = ''.join([x for x in basename if x not in
                                          forbidden])
    return entry
