# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import logging
import urllib.request, urllib.error, urllib.parse
from os import path
from sys import exit

import feedparser
import time

from poco.output import Outcome
from poco import history
from poco import files


logger = logging.getLogger('POCA')


def attach_size(self, mega):
    '''Expands entry with url and size'''
    self['valid'] = True
    try:
        self['poca_url'] = self.enclosures[0]['href']
    except (KeyError, IndexError, AttributeError):
        self['valid'] = False
        return
    try:
        self['poca_size'] = int(self.enclosures[0]['length'])
        if self['poca_size'] == 0:
            raise ValueError
    except (KeyError, ValueError):
        try:
            f = urllib.request.urlopen(self['poca_url'])
            self['poca_size'] = int(f.info()['Content-Length'])
            f.close()
        except (urllib.error.HTTPError, urllib.error.URLError):
            self['valid'] = False
    if self['valid']:
        self['poca_mb'] = round(self.poca_size / mega, 2)

def attach_path(self, sub):
    '''Expands entry with file name and path'''
    parsed_url = urllib.parse.urlparse(self['poca_url'])
    self['poca_filename'] = path.basename(parsed_url.path)
    self['poca_abspath'] = path.join(sub.sub_dir, self['poca_filename'])

feedparser.FeedParserDict.attach_size = attach_size
feedparser.FeedParserDict.attach_path = attach_path


class Channel:
    def __init__(self, config, sub):
        '''A class for a single subscription/channel. Creates the containers
        first, then acts on them and updates the db as it goes.'''
        
        self.sub = sub
        self.title = sub.title.upper() + '. '

        # see that we can write to the designated directory
        outcome = files.check_path(sub.sub_dir)
        if not outcome.success:
            logger.error(self.title + outcome.msg)
            exit()

        # create containers: feed, jar, combo, wanted
        self.jar, outcome = history.get_jar(config.paths, self.sub)
        if not outcome.success:
            logger.error(self.title + outcome.msg)
            exit()
        self.feed = Feed(self.sub, self.jar)
        if not self.feed.outcome.success:
            logger.error(self.title + self.feed.outcome.msg)
            return 
        self.combo = Combo(self.feed, self.jar)
        self.wanted = Wanted(self.sub, self.combo)
        self.unwanted = set(self.jar.lst) - set(self.wanted.lst)
        self.lacking = set(self.wanted.lst) - set(self.jar.lst)
        msg = self.title
        if len(self.unwanted) > 0:
            msg = msg + str(len(self.unwanted)) + ' to be removed. ' 
        if len(self.lacking) > 0:
            msg = msg + str(len(self.lacking)) + ' to be downloaded.'
        if len(self.unwanted) == 0 and len(self.lacking) == 0:
            msg = msg + 'No changes.'
        logger.info(msg)
        self.removed, self.downed, self.failed = [], [], []

        # loop through unwanted (set) entries to remove
        for uid in self.unwanted:
            entry = self.jar.dic[uid]
            self.remove(uid, entry)
            logger.debug('  -  ' + entry['poca_filename'])
            self.removed.append(entry['poca_filename'])

        # loop through wanted entries (list) to download
        # Looping through the lacking entries, we insert them at the
        # index they have in wanted.lst. By the time we get to old ones,
        # they will have the correct index. This has been found to 
        # be preferable to a) starting a new list based on wanted 
        # and b) inserting all new entries at the front.
        for uid in self.wanted.lst:
            if uid not in self.lacking:
                continue
            entry = self.wanted.dic[uid]
            wantedindex = self.wanted.lst.index(uid)
            outcome = files.download_audio_file(entry)
            if outcome.success:
                # this is where we override the downloaded file's metadata:
                # files.tag_audio_file
                self.add_to_jar(uid, entry, wantedindex)
                logger.debug('  +  ' + entry['poca_filename'])
                self.downed.append(entry['poca_filename'])
            else:
                logger.debug('  %  ' + entry['poca_filename'])
                self.failed.append(entry['poca_filename'])

        # print summary to log ('warn' is filtered out in stream)
        if self.downed:
            logger.warn(self.title + 'Downloaded: ' + ', '.join(self.downed))
        if self.failed:
            logger.warn(self.title + 'Failed: ' + ', '.join(self.failed))
        if self.removed:
            logger.warn(self.title + 'Removed: ' + ', '.join(self.removed))

    def add_to_jar(self, uid, entry, wantedindex):
        '''Add new entry to jar'''
        self.jar.lst.insert(wantedindex, uid)
        self.jar.dic[uid] = entry
        outcome = self.jar.save()
        if not outcome.success:
            logger.error(self.title + outcome.msg)
            exit()

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the jar'''
        outcome = files.delete_file(entry['poca_abspath'])
        if not outcome.success:
            logger.error(self.title + outcome.msg)
            exit()
        self.jar.lst.remove(uid)
        del(self.jar.dic[uid])
        outcome = self.jar.save()
        if not outcome.success:
            logger.error(self.title + outcome.msg)
            exit()


class Feed:
    def __init__(self, sub, jar):
        '''Constructs a container for feed entries'''
        try:
            doc = feedparser.parse(sub.url)
        except TypeError:
            # https://github.com/kurtmckee/feedparser/issues/30#issuecomment-183714444            
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                doc = feedparser.parse(sub.url)
            else:
                raise
        # only bozo for actual errors
        if doc.bozo and not doc.entries and doc.status != 304:            
            self.outcome = Outcome(False, 'Error: ' + str(doc.bozo_exception))
            return
        # if etag is 304, doc.entries is empty and we proceed as normal
        if doc.has_key('etag'):
            jar.etag = doc.etag
            jar.save()
        self.lst = [ entry.id for entry in doc.entries ]
        self.dic = { entry.id : entry for entry in doc.entries }
        self.outcome = Outcome(True, 'Got feed.')

class Combo:
    def __init__(self, feed, jar):
        '''Constructs a container holding all combined feed and jar 
        entries. Copies feed then adds non-duplicates from jar'''
        self.lst = list(feed.lst)
        self.lst.extend(x for x in jar.lst if x not in feed.lst)
        self.dic = feed.dic.copy()
        self.dic.update(jar.dic)

class Wanted():
    def __init__(self, sub, combo):
        '''Constructs a container for all the entries we have room for, 
        regardless of where they are, internet or local folder.'''
        self.lst, self.dic = [], {}
        mega = 1048576.0
        self.max_bytes = int(sub.max_mb) * mega
        self.cur_bytes = 0
        for uid in combo.lst:
            entry = combo.dic[uid]
            if 'valid' not in entry:
                entry.attach_size(mega)
                if not entry.valid:
                    continue
            if self.cur_bytes + entry.poca_size < self.max_bytes:
                self.cur_bytes += entry.poca_size
                # run metadata adjustment method on entry
                entry.attach_path(sub)
                self.lst.append(uid)
                self.dic[uid] = entry
            else:
                break

