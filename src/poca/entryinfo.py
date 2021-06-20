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
import unicodedata
from os import path
import urllib.request
import urllib.error
import urllib.parse


# ####################################### #
# VALIDATION                              #
# ####################################### #

def validate(entry):
    '''validates entry if it contains an enclosure'''
    entry['expanded'], entry['valid'] = False, False
    try:
        entry['poca_url'] = entry.enclosures[0]['href']
        parsed_url = urllib.parse.urlparse(entry['poca_url'])
        parsed_path = urllib.parse.unquote(parsed_url.path)
        entry['org_filename'] = path.basename(parsed_path)
        basename, dotextension = path.splitext(entry['org_filename'])
        entry['basename'] = basename
        entry['extension'] = dotextension[1:]
        entry['valid'] = True
        #entry.pop('org_filename')
    except (KeyError, IndexError, AttributeError):
        pass
    return entry


# ####################################### #
# EXPANSION                               #
# ####################################### #

def expand(entry, sub, sub_dir):
    '''expands entry with url, paths and size'''
    if entry['expanded'] is True:
        return entry
    entry['sub_title'] = sub.title.text
    entry['directory'] = sub_dir
    entry['poca_mb'] = info_megabytes(entry)
    #entry['metadata'] = "Coming soon"
    entry['user_vars'] = info_user_vars(entry)
    entry['rename'] = sub.rename if hasattr(sub, 'rename') else None
    entry['names'] = names(entry)
    # NOTE: 'poca_filename' used to be the filename to be written to.
    #       Now it just serves as a way to check if multiple entries stand
    #       to get the same filename. Actual filename is chosen from
    #       candidates in entry['names'] at time of download.
    entry['poca_filename'] = '.'.join((entry['names']['base'], entry['extension']))
    entry['expanded'] = True
    return entry

def info_megabytes(entry):
    '''expand with info about length and size stats'''
    try:
        _bytes = int(entry.enclosures[0]['length'])
        megabytes = round(_bytes / 1048576.0, 2) or None
    except (KeyError, ValueError, TypeError) as e:
        megabytes = None
    return megabytes

def info_user_vars(entry):
    '''expand with info that the user can use in renaming'''
    # check with rss specs and feedparser to see what can be relied on
    user_vars = {}
    try:
        date = time.strftime('%Y-%m-%d', entry['published_parsed'])
    except (KeyError, TypeError):
        date = '1970-01-01'
    user_vars['date'] = date
    user_vars['title'] = entry['sub_title']
    # title and id are both optional elements of at least rss spec :/
    user_vars['episode_title'] = str(entry['title'])
    user_vars['uuid'] = uuid.uuid4().hex[:9]
    user_vars['uid'] = entry['id'] if hasattr(entry, 'id') else \
                       user_vars['uuid']
    # is it foolish to assume they are always there?
    user_vars['org_name'] = entry['basename']
    #print(user_vars)
    return user_vars


# ####################################### #
# NAMING                                  #
# ####################################### #

def names(entry):
    '''generates a dictionary of file names of decreasing permissiveness'''
    user_vars = entry['user_vars']
    if entry['rename'] is not None:
        name_children = [el for el in entry['rename'].iterchildren()]
        name_tags = [el.tag for el in name_children if el.tag in user_vars]
        # note: if a used key is not in user_vars, it is silently discarded
        # so: a user misspelling a key will possibly end up with a zero-length
        # filename. that will result in using the fallback name and be
        # difficult to understand why that happens.
        name_lst = [user_vars[tag] for tag in name_tags]
        divider = entry['rename'].get('divider') or ' '
        space = entry['rename'].get('space') or ' '
        name_base = divider.join(name_lst).replace(' ', space)
    else:
        name_base = user_vars['org_name']
    name_dic = {}
    name_dic['base'] = name_base
    name_dic['permissive'] = filename_permissive(name_base)
    name_dic['ntfs'] = filename_ntfs(name_base)
    name_dic['restrictive'] = filename_restrictive(name_base)
    name_dic['fallback'] = '-'.join((user_vars['date'], user_vars['uuid']))
    #print(name_dic)
    return name_dic

def filename_permissive(name_base):
    '''produces filenames that are allowed on most linux filesystems'''
    # no null, no forward slash
    forbidden = '[\x00\x2f]'
    re_permissive = re.compile(forbidden)
    permissive = re_permissive.sub('', name_base)
    return permissive

def filename_ntfs(name_base):
    '''produces filenames that are allowed on ntfs/vfat filesystems'''
    # forbidden chars: " * / : < > ? \ |
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
    re_whitespace = re.compile('\s')
    re_restrictive = re.compile(forbidden)
    restrictive = re_whitespace.sub('_', name_base)
    restrictive = re_restrictive.sub('', restrictive)
    return restrictive
