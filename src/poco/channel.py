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
#from time import sleep

import feedparser

from poco.output import Outcome
from poco import history
from poco import files


logger = logging.getLogger('POCA')

class Channel:
    def __init__(self, config, sub):
        '''A class for a single subscription/channel. Creates the containers
        first, then acts on them and updates the db as it goes.'''
        
        self.sub = sub

        # see that we can write to the designated directory
        outcome = files.check_path(sub.sub_dir)
        if not outcome.success:
            logger.error(outcome.msg)
            exit()

        # create containers: feed, jar, combo, wanted
        self.feed = Feed(self.sub)
        if not self.feed.outcome.success:
            logger.error(self.sub.title + ': ' + self.feed.outcome.msg)
            return 
        self.jar = history.get_jar(config.paths, self.sub)
        self.combo = Combo(self.feed, self.jar)
        self.wanted = Wanted(self.sub, self.combo)
        self.unwanted = list(set(self.jar.lst) - set(self.wanted.lst))
        self.lacking = list(set(self.wanted.lst) - set(self.jar.lst))
        self.keeping = list(set(self.wanted.lst) - set(self.lacking))
        logger.info(self.sub.title.upper() + '. ' +
            str(len(self.unwanted)) + ' to be removed. ' +
            str(len(self.lacking)) + ' to be downloaded.')
        self.removed, self.downloaded = [], []

        # loop through unwanted entries to remove
        for uid in self.unwanted:
            entry = self.jar.dic[uid]
            del_outcome, jar_outcome  = self.remove(uid, entry)
            if not jar_outcome.success and del_outcome.success:
                logger.error(jar_outcome.msg + ' ' + del_outcome.msg)
                exit()
            logger.debug('  -- ' + entry['poca_filename'])
            self.removed.append(entry['poca_filename'])

        # loop through wanted entries to download or check
        self.new_jar = history.Jar(config.paths, self.sub)
        for uid in self.keeping:
            self.add_to_jar(uid)
        for uid in self.lacking:
            entry = self.wanted.dic[uid]
            outcome = files.download_audio_file(entry)
            if outcome.success:
                self.add_to_jar(uid)
                logger.debug('  ++ ' + entry['poca_filename'])
                self.downloaded.append(entry['poca_filename'])

    def add_to_jar(self, uid):
        '''Add keeper/getter to new jar (do we need to test for
        outcome? Isn't success guaranteed at this point?)'''
        entry = self.wanted.dic[uid]
        self.new_jar.lst.append(uid)
        self.new_jar.dic[uid] = entry
        jar_outcome = self.new_jar.save()
        if not jar_outcome.success:
            logger.error(outcome.msg)
            exit()

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the old jar
        (in the event that the program is interrupted in between
        deletion and writing a new jar to the db file)'''
        del_outcome = files.delete_file(entry['poca_abspath'])
        self.jar.lst.remove(uid)
        jar_outcome = self.jar.save()
        return (del_outcome, jar_outcome)

    def check(self, uid, entry, args):
        '''Performs a quick check-up on existing keeper-files and removes 
        the entry from the old jar'''
        msg1 = ' Checking existing file:  ' + entry['poca_filename']
        if path.isfile(entry['poca_abspath']):
            self.put.cols(msg1, 'OK')
            outcome = Outcome(True, 'file ok')
        else:
            self.put.cols(msg1, 'FILE NOT FOUND. Attempting download.')
            outcome = files.download_audio_file(args, entry)
        self.jar.lst.remove(uid)
        return outcome

class Feed:
    def __init__(self, sub):
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
        if not doc.feed:
            self.outcome = Outcome(False, str(doc.bozo_exception))
            return
        self.lst = [ entry.id for entry in doc.entries ]
        self.dic = { entry.id : entry for entry in doc.entries }
        self.outcome = Outcome(True, 'Got feed')

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
        self.lst, self.dic = ( [], {} )
        mega = 1048576.0
        self.max_bytes = int(sub.max_mb) * mega
        self.cur_bytes = 0

        for uid in combo.lst:
            # looks like we're re-doing old data entries as well as new
            # why? can't we just tag new ones? or old ones?
            entry = combo.dic[uid]
            try:
                entry['poca_url'] = entry.enclosures[0]['href']
            except (KeyError, IndexError, AttributeError):
                continue
            entry['poca_size'] = self.get_size(entry)
            if not entry['poca_size']:
                continue
            entry['poca_mb'] = round(entry.poca_size / mega, 2)
            entry['poca_filename'] = self.get_filename(entry)
            entry['poca_abspath'] = path.join(sub.sub_dir, 
                entry['poca_filename'])
            if self.cur_bytes + entry.poca_size < self.max_bytes:
                self.cur_bytes += entry.poca_size
                self.lst.append(uid)
                self.dic[uid] = entry
            else:
                break

    def get_size(self, entry):
        '''Returns the entrys size in bytes. Tries to get if off of the
        enclosure, otherwise pokes url for info.'''
        try:
            size = int(entry.enclosures[0]['length'])
            if size == 0:
                raise ValueError
        except (KeyError, ValueError):
            try:
                f = urllib.request.urlopen(entry['poca_url'])
                size = int(f.info()['Content-Length'])
                f.close()
            except (urllib.error.HTTPError, urllib.error.URLError):
                size = False
        return size

    def get_filename(self, entry):
        '''Parses URL to find base filename. To be expanded with naming
        options'''
        parsed_url = urllib.parse.urlparse(entry['poca_url'])
        filename = path.basename(parsed_url.path)
        return filename

