#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import urllib2
from os import path
from urlparse import urlparse

import feedparser

from poco import output
from poco import history
from poco import files


class Channel:
    def __init__(self, config, out, sub):
        '''A class for a single subscription/channel. Creates the containers
        first, then acts on them and updates the db as it goes.'''
        self.sub, self.out = sub, out
        self.out.head(sub.title)

        self.feed = Feed(self.sub)
        self.jar = history.get_jar(config.paths, self.sub)
        self.combo = Combo(self.feed, self.jar)
        self.wanted = Wanted(self.sub, self.combo, logger)

        for uid in list(set(self.jar.lst) - set(self.wanted.lst)):
            outcome = self.remove(uid, self.jar.dic[uid])
        self.new_jar = history.Jar(config.paths, self.sub)
        for uid in self.wanted.lst:
            entry = self.wanted.dic[uid]
            if uid not in self.jar.lst:
                outcome = files.download_audio_file(config.args, entry)
            else:
                outcome = self.check(uid, entry, config.args)
            if outcome.success:
                self.new_jar.lst.append(uid)
                self.new_jar.dic[uid] = entry
                self.new_jar.save()
            else:
                self.out.single(' Something went wrong. Entry has been skipped')
        # should any - by mistake - remain in the old jar (i.e. not have been 
        # either removed or renewed) we dispense with them.
        for uid in self.jar.lst:
            entry = self.jar.dic[uid]
            outcome = self.remove(uid, entry, config.args)
            self.out.single(' Entry ' + entry.title + 'appears to have fallen ' +
                'through the cracks. This should not happen. Entry has been ' +
                'deleted. If this happens repeatedly, please consider ' +
                'tipping off the developer.')
        self.out.single('')

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the old jar'''
        msg1 = (' Removing existing file:  ' + entry['poca_filename'])
        outcome = files.delete_file(entry['poca_abspath'])
        if outcome.success:
            self.out.cols(msg1, 'OK')
        else:
            self.out.cols(msg1, 'FILE NOT FOUND. Please check manually.')
        self.jar.lst.remove(uid)
        dummy = self.jar.dic.pop(uid)
        self.jar.save()
        return outcome

    def check(self, uid, entry, args):
        '''Performs a quick check-up on existing keeper-files and removes 
        the entry from the old jar'''
        msg = (' Checking existing file:  ' + entry['poca_filename'])[0:60]
        msg = (msg + ' ').ljust(63, '.') + ' '
        if path.isfile(entry['poca_abspath']):
            self.logger.info(msg + 'OK')
            outcome = output.Outcome(True, 'file ok')
        else:
            self.logger.info(msg + 'FILE NOT FOUND. Attempting download.')
            outcome = files.download_audio_file(args, entry)
        self.jar.lst.remove(uid)
        dummy = self.jar.dic.pop(uid)
        return outcome

class Feed:
    def __init__(self, sub):
        '''Constructs a container for feed entries'''
        doc = feedparser.parse(sub.url)
        # note: some feeds do not have entry id's (?) The times bugle (old)
        # for one failed. Check feedparser documentation.
        self.lst = [ entry.id for entry in doc.entries ]
        self.dic = { entry.id : entry for entry in doc.entries }

class Combo:
    def __init__(self, feed, jar):
        '''Constructs a container holding all combined feed and jar 
        entries. Copies feed then adds non-duplicates from jar'''
        self.lst = list(feed.lst)
        self.lst.extend(x for x in jar.lst if x not in feed.lst)
        self.dic = feed.dic.copy()
        self.dic.update(jar.dic)

class Wanted():
    def __init__(self, sub, combo, logger):
        '''Constructs a container for all the entries we have room for, 
        regardless of where they are, internet or local folder.'''
        self.lst, self.dic = ( [], {} )
        mega = 1048576.0
        self.max_bytes = int(sub.max_mb) * mega
        self.cur_bytes = 0

        for uid in combo.lst:
            entry = combo.dic[uid]
            entry['poca_url'] = entry.enclosures[0]['href']
            entry['poca_size'] = self.get_size(entry)
            entry['poca_mb'] = str(round(entry.poca_size / mega, 2)) + ' Mb'
            entry['poca_filename'] = self.get_filename(entry)
            entry['poca_abspath'] = path.join(sub.sub_dir, 
                entry['poca_filename'])
            if self.cur_bytes + entry.poca_size < self.max_bytes:
                self.cur_bytes += entry.poca_size
                self.lst.append(uid)
                self.dic[uid] = entry
                msg = (' Adding to wanted list:   ' + entry.title)[0:60] + ' '
                msg = msg.ljust(63, '.') + ' ' + entry['poca_mb']
                logger.info(msg)
            else:
                break
        total_mb = str(round(self.cur_bytes / mega, 2)) + ' Mb'
        logger.info(' Total size: '.ljust(63, '.') + ' ' + total_mb)
        max_mb = str(round(self.max_bytes / mega, 2)) + ' Mb'
        logger.info(' Allotted space: '.ljust(63, '.') + ' ' + max_mb + '\n')

    def get_size(self, entry):
        '''Returns the entrys size in bytes. Tries to get if off of the
        enclosure, otherwise pokes url for info.'''
        try:
            size = int(entry.enclosures[0]['length'])
        except KeyError:
            f = urllib2.urlopen(entry['poca_url'])
            size = int(f.info()['Content-Length'])
            f.close()
        return size

    def get_filename(self, entry):
        '''Parses URL to find base filename. To be expanded with naming
        options'''
        parsed_url = urlparse(entry['poca_url'])
        filename = path.basename(parsed_url.path)
        return filename

