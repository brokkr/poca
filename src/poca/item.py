# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Get more information on a single feed entry"""
# (we use 'entry' for the feedparser.entries[i] dictionary,
# and 'item' for our own class instances built upon them)

import re
import sys
import time
import uuid
import unicodedata
import urllib.request
import urllib.error
import urllib.parse

from os import path
from pathlib import Path


class Item:
    def __init__(self, entry):
        self.type_feed = True
        self.type_current = False
        self.type_blocked = False
        self.stage_valid = False
        self.stage_wanted = False
        self.stage_included = False
        self.end_removed = False
        self.end_retrieved = False
        self.entry = entry
        self.title = self.entry['title']
        self.guid = entry.guid
        self.variables = {}
        self.names = {}

    def validate(self):
        '''validates item if entry contains an enclosure with parsable url'''
        try:
            self.url = self.entry.enclosures[0]['href']
            parsed_url = urllib.parse.urlparse(self.url)
            parsed_path = urllib.parse.unquote(parsed_url.path)
            self.org_filename = path.basename(parsed_path)
            self.stage_valid = True
        except (KeyError, IndexError, AttributeError):
            pass

    def filter_vars(self):
        '''retrieves filter variables from entry'''
        self.variables['date'] = self.entry['published_parsed']
        self.variables['weekday'] = self.entry['published_parsed'].tm_wday
        self.variables['hour'] = self.entry['published_parsed'].tm_hour
        self.variables['title_episode'] = self.entry['title']
        self.variables['filename'] = self.org_filename

    def extra_vars(self, sub, feed):
        '''expand with info that the user can use in renaming'''
        try:
            self.variables['date_str'] = time.strftime('%Y-%m-%d',
                self.entry['published_parsed'])
        except (KeyError, TypeError):
            self.variables['date_str'] = '1970-01-01'
        self.variables['title_sub'] = sub['title']
        self.variables['title_feed'] = feed.title
        self.variables['author_feed'] = feed.author if hasattr(feed,
            'author') else 'No feed author'
        self.variables['author_entry'] = self.entry.author if \
            hasattr(self.entry, 'author') else 'No entry author'
        self.variables['uuid'] = uuid.uuid4().hex[:9]
        self.variables['guid'] = self.entry['guid']
        self.variables['basename'], self.variables['extension'] = \
            path.splitext(self.org_filename)

    def generate_names(self, base_dir, sub):
        '''generates a dictionary of file names of decreasing permissiveness'''
        if 'rename' in sub:
            name_tags = [tag for tag in sub['rename'] if tag in self.variables]
            # note: if a used key is not in user_vars, it is silently discarded
            # so: a user misspelling a key will possibly end up with a zero-length
            # filename. that will result in using the fallback name and be
            # difficult to understand why that happens.
            name_lst = [str(self.variables[tag]) for tag in name_tags]
            divider = ' - '
            space = ' '
            name_base = divider.join(name_lst).replace(' ', space)
        else:
            name_base = self.variables['basename']
        self.names['base'] = (base_dir,
                              sub['title'],
                              name_base,
                              self.variables['extension'])
        self.names['permissive'] = (base_dir,
                                    self.filename_permissive(sub['title']),
                                    self.filename_permissive(name_base),
                                    self.variables['extension'])
        self.names['ntfs'] = (base_dir,
                              self.filename_ntfs(sub['title']),
                              self.filename_ntfs(name_base),
                              self.variables['extension'])
        self.names['restrictive'] = (base_dir,
                                     self.filename_restrictive(sub['title']),
                                     self.filename_restrictive(name_base),
                                     self.variables['extension'])
        self.names['fallback'] = (base_dir,
                                  self.filename_restrictive(sub['title']),
                                  '-'.join((self.variables['date_str'],
                                            self.variables['uuid'])),
                                  self.variables['extension'])
        self.name_test = ''.join((name_base, self.variables['extension']))
        #print(self.names)

    def filename_permissive(self, name_base):
        '''produces filenames that are allowed on most linux filesystems'''
        # no null, no forward slash
        forbidden = '[\x00\x2f]'
        re_permissive = re.compile(forbidden)
        permissive = re_permissive.sub('', name_base)
        return permissive

    def filename_ntfs(self, name_base):
        '''produces filenames that are allowed on ntfs/vfat filesystems'''
        # forbidden chars: " * / : < > ? \ |
        forbidden = '[\x22\x2a\x2f\x3a\x3c\x3e\x3f\x5c\x7c]'
        re_ntfs = re.compile(forbidden)
        ntfs = re_ntfs.sub('', name_base)
        # no control characters
        ntfs = ''.join(x for x in ntfs if unicodedata.category(x)[0] != 'C')
        return ntfs

    def filename_restrictive(self, name_base):
        '''produces filenames that should not fall foul of any current protocols'''
        # only alphanumerical, hyphens and underscores allowed
        forbidden = '[^a-zA-Z0-9\x5f\x2d]'
        re_whitespace = re.compile('\s')
        re_restrictive = re.compile(forbidden)
        restrictive = re_whitespace.sub('_', name_base)
        restrictive = re_restrictive.sub('', restrictive)
        return restrictive

    def size_vars(self):
        '''expand with info about length and size stats'''
        try:
            size_bytes = int(self.entry.enclosures[0]['length'])
            self.size_mb = round(size_bytes / 1048576.0, ndigits=None) or None
        except (KeyError, ValueError, TypeError) as e:
            self.size_mb = None

class CurrentItem(Item):
    def __init__(self, guid, state_entry):
        self.type_feed = False
        self.type_current = True
        self.type_blocked = False
        self.stage_valid = False
        self.stage_wanted = False
        self.stage_included = False
        self.end_removed = False
        self.end_retrieved = False
        self.guid = guid
        self.entry = None
        self.path = state_entry['path']
        self.variables = state_entry['variables']
        self.names = {}
        self.title = self.variables['title_episode']

    def validate(self):
        '''where FeedItem's validate check's url, CurrentItem's validate
           should check for file existence'''
        self.stage_valid = True

    def filter_vars(self):
        pass

    def extra_vars(self, sub, feed):
        pass

    def size_vars(self):
        pass

class BlockedItem():
    def __init__(self, guid):
        '''simple item which only need to block feed items'''
        # it could in principle subclass Item but there's not much need
        self.type_feed = False
        self.type_current = False
        self.type_blocked = True
        self.stage_valid = False
        self.stage_wanted = False
        self.stage_included = False
        self.end_removed = False
        self.end_retrieved = False
        self.guid = guid
        self.title = str()
        self.entry = None
