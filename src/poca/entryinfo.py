# -*- coding: utf-8 -*-

# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Get more information on a single feed entry"""

import re
import sys
import time
import uuid
from os import path
import urllib.request
import urllib.error
import urllib.parse


def validate(entry):
    '''Validates entry if it contains an enclosure'''
    entry['expanded'], entry['valid'] = False
    try:
        entry['poca_url'] = entry.enclosures[0]['href']
        entry['valid'] = True
    except (KeyError, IndexError, AttributeError):
        pass
    return entry

def info_filename(entry, sub_dir):
    '''expand with info about filename'''
    parsed_url = urllib.parse.urlparse(entry['poca_url'])
    parsed_path = urllib.parse.unquote(parsed_url.path)
    entry['filename'] = path.basename(parsed_path)
    entry['poca_basename'], _ext = path.splitext(entry['filename'])
    entry['poca_ext'] = _ext[1:]
    entry['sub_dir'] = sub_dir
    return entry

def info_stats(entry):
    '''expand with info about length and size stats'''
    try:
        entry['poca_size'] = int(entry.enclosures[0]['length'])
        if entry['poca_size'] == 0:
            raise ValueError
        entry['poca_mb'] = round(entry.poca_size / 1048576.0, 2)
    except (KeyError, ValueError, TypeError):
        entry['poca_size'] = None
        entry['poca_mb'] = None
    return entry

def info_user_vars(entry, sub):
    '''expand with info that the user can use in renaming'''
    # check with rss specs and feedparser to see what can be relied on
    try:
        date = time.strftime('%Y-%m-%d', entry['published_parsed'])
    except (KeyError, TypeError):
        date = 'missing_pub_date'
    user_vars = {'original_filename': entry['poca_basename'],
                 'subscription_title': sub.title.text,
                 'episode_title': str(entry['title']),
                 'uid': entry['id'],
                 'date': date,
                 'org_name': entry['poca_basename'],
                 'title': sub.title.text}
    entry['user_vars'] = user_vars
    return entry

def expand(entry, sub, sub_dir):
    '''Expands entry with url, paths and size'''
    if entry['expanded'] is True:
        return entry
    entry = info_filename(entry, sub_dir)
    entry = info_stats(entry)
    entry = info_user_vars(entry, sub)
    entry['rename'] = sub.rename if hasattr(sub, 'rename') else None
    entry['names'] = names(entry)
    entry['expanded'] = True
    return entry

def filename_permissive(name_base):
    '''produces filenames that are allowed on most linux filesystems'''
    # no null, no forward slash
    forbidden = '[\x00\x2f]'
    re_permissive = re.compile(forbidden)
    permissive = re_permissive.sub('', name_base)
    return permissive

def filename_ntfs(name_base):
    '''produces filenames that are allowed on ntfs/vfat filesystems'''
    #forbidden chars: " * / : < > ? \ |
    forbidden = '[\x22\x2a\x2f\x3a\x3c\x3e\x3f\x5c\x7c]'
    re_ntfs = re.compile(forbidden)
    ntfs = re_ntfs.sub('', name_base)
    # no control characters
    ntfs = ''.join(x for x in ntfs if unicodedata.category(x)[0] != 'C')
    return ntfs

def filename_restrictive(name_base):
    '''produces filenames that should not fall foul of any current protocols'''
    # only alphanumerical, hyphens and underscores allowed
    forbidden = '[^a-zA-Z0-9\x5f\x2d]'
    re_restrictive = re.compile(forbidden)
    restrictive = re_restrictive.sub('', name_base)
    return restrictive

def names(entry):
    user_vars = entry['user_vars']
    if entry['rename']:
        name_children = [el for el in entry['rename'].iterchildren()]
        name_tags = [el.tag for el in name_children if el.tag in user_vars]
        name_lst = [user_vars[tag] for tag in name_tags]
        divider = ['entry']rename.get('divider') or ' '
        space = ['entry']rename.get('space') or ' '
        name_base = divider.join(name_lst).replace(' ', space)
    else:
        name_base = user_vars['org_name']
    name_dic = {}
    name_dic['base'] = name_base
    name_dic['permissive'] = filename_permissive(name_base)
    name_dic['ntfs'] = filename_ntfs(name_base)
    name_dic['restrictive'] = filename_restrive(name_base)
    name_dic['fallback'] = uuid.uuid4().hex[:8]
    return name_dic
