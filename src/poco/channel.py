# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import sys

import feedparser

from poco import files, history, entry, output, tag
from poco.outcome import Outcome


feedparser.FeedParserDict.attach_size = entry.attach_size
feedparser.FeedParserDict.attach_path = entry.attach_path


class Channel:
    def __init__(self, config, sub, bump=False):
        '''A class for a single subscription/channel. Creates the containers
        first, then acts on them and updates the db as it goes.'''
        
        self.sub = sub
        self.title = sub.title.upper()
        self.config = config

        # see that we can write to the designated directory
        outcome = files.check_path(sub.sub_dir)
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()

        # get feed and jar and create collections (wanted, unwanted, etc.)
        self.jar, outcome = history.get_jar(config.paths, self.sub)
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()
        self.feed = Feed(self.sub, self.jar)
        if not self.feed.outcome.success:
            output.suberror(self.title, self.feed.outcome)
            return 
        self.combo = Combo(self.feed, self.jar, self.sub)
        self.wanted = Wanted(self.sub, self.combo, self.jar, bump)
        self.unwanted = set(self.jar.lst) - set(self.wanted.lst)
        self.lacking = set(self.wanted.lst) - set(self.jar.lst)
        output.plans(self.title, len(self.unwanted), len(self.lacking))
        self.removed, self.downed, self.failed = [], [], []

        # loop through unwanted (set) entries to remove
        for uid in self.unwanted:
            entry = self.jar.dic[uid]
            self.remove(uid, entry)

        # loop through wanted (list) entries to acquire
        for uid in self.wanted.lst:
            if uid not in self.lacking:
                continue
            entry = self.wanted.dic[uid]
            self.acquire(uid, entry)

        # download cover image
        if self.downed and self.feed.image:
            outcome = files.download_file(self.feed.image, sub.image_path)

        # print summary of operations in file log
        output.summary(self.title, self.downed, self.removed, self.failed)

    def acquire(self, uid, entry):
        '''Get new entries, tag them and add to history'''
        # loop through wanted entries (list) to download
        # Looping through the lacking entries, we insert them at the
        # index they have in wanted.lst. By the time we get to old ones,
        # they will have the correct index. This has been found to 
        # be preferable to a) starting a new list based on wanted 
        # and b) inserting all new entries at the front.
        output.downloading(entry)
        wantedindex = self.wanted.lst.index(uid) - len(self.failed)
        outcome = files.download_file(entry['poca_url'], entry['poca_abspath'])
        if outcome.success:
            outcome = tag.tag_audio_file(self.config.prefs, self.sub, entry)
            if not outcome.success:
                output.tag_fail(outcome)
            self.add_to_jar(uid, entry, wantedindex)
            self.downed.append(entry['poca_filename'])
        else:
            # if a download fails, len(self.failed) is subtracted
            # from wanted index of following files to keep order
            output.dl_fail(outcome)
            self.failed.append(entry['poca_filename'])

    def add_to_jar(self, uid, entry, wantedindex):
        '''Add new entry to jar'''
        self.jar.lst.insert(wantedindex, uid)
        self.jar.dic[uid] = entry
        if hasattr(self.sub, 'from_the_top'):
            self.jar.bookmark += 1
        outcome = self.jar.save()
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the jar'''
        output.removing(entry)
        outcome = files.delete_file(entry['poca_abspath'])
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()
        self.jar.lst.remove(uid)
        del(self.jar.dic[uid])
        outcome = self.jar.save()
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()
        self.removed.append(entry['poca_filename'])


class Feed:
    def __init__(self, sub, jar):
        '''Constructs a container for feed entries'''
        try:
            old_etag = jar.etag
        except AttributeError:
            old_etag = None
        try:
            doc = feedparser.parse(sub.url, etag=old_etag)
        except TypeError:
            # https://github.com/kurtmckee/feedparser/issues/30#issuecomment-183714444            
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                doc = feedparser.parse(sub.url, etag=old_etag)
            else:
                raise
        # only bozo for actual errors
        if doc.bozo and not doc.entries:
            if 'status' in doc:
                # if etag is 304 doc.entries is empty and we proceed as normal
                if doc.status != 304:
                    self.outcome = Outcome(False, str(doc.bozo_exception))
                    return
            else:
                self.outcome = Outcome(False, str(doc.bozo_exception))
                return
        if doc.has_key('etag'):
            jar.etag = doc.etag
            jar.save()
        try:
            self.lst = [ entry.id for entry in doc.entries ]
            self.dic = { entry.id : entry for entry in doc.entries }
        except (KeyError, AttributeError):
            try:
                self.lst = [ entry.enclosures[0]['href'] 
                    for entry in doc.entries ]
                self.dic = { entry.enclosures[0]['href'] : entry 
                    for entry in doc.entries }
            except (KeyError, AttributeError):
                self.outcome = Outcome(False, 'Cant find entries in feed.')
        if hasattr(sub, 'from_the_top'):
            self.lst.reverse()
        try:
            self.image = doc.feed.image['href']
        except (AttributeError, KeyError):
            self.image = None
        self.outcome = Outcome(True, 'Got feed.')

class Combo:
    def __init__(self, feed, jar, sub):
        '''Constructs a container holding all combined feed and jar 
        entries. Copies feed then adds non-duplicates from jar'''
        if hasattr(sub, 'from_the_top'):
            self.lst = list(jar.lst)
            self.lst.extend(x for x in feed.lst if x not in jar.lst)
        else:
            self.lst = list(feed.lst)
            self.lst.extend(x for x in jar.lst if x not in feed.lst)
        self.dic = feed.dic.copy()
        self.dic.update(jar.dic)

class Wanted():
    def __init__(self, sub, combo, jar, bump):
        '''Constructs a container for all the entries we have room for, 
        regardless of where they are, internet or local folder.'''
        self.lst, self.dic = [], {}
        mega = 1048576.0
        self.max_bytes = float(sub.max_mb) * mega
        self.cur_bytes = 0
        if hasattr(sub, 'from_the_top') and bump:
            combo.lst = combo.lst[jar.bookmark:]
        if sub.max_no:
            combo.lst = combo.lst[:int(sub.max_no)]
        for uid in combo.lst:
            entry = combo.dic[uid]
            if 'valid' not in entry:
                entry.attach_size(mega)
                if not entry.valid:
                    continue
            if self.cur_bytes + entry.poca_size < self.max_bytes:
                self.cur_bytes += entry.poca_size
                entry.attach_path(sub)
                self.lst.append(uid)
                self.dic[uid] = entry
            else:
                break

