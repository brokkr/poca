#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import time
import urllib2
from os import path
from urlparse import urlparse

import feedparser

from poco import output
from poco import history
from poco import files


class Channel:
    def __init__(self, config, logger, sub):
        '''A class for a single subscription/channel'''
        self.sub, self.logger = sub, logger
        self.logger.info(sub.title.upper())
        # Find all available entries
        self.feed = Feed(self.sub)
        self.jar = history.get_jar(config.paths, self.sub)
        self.combo = Combo(self.feed, self.jar)
        # Find all the ones we want (and don't want)
        self.wanted = Wanted(self.sub, self.combo, logger)
        self.unwanted = Unwanted(self.jar, self.wanted)
        # Act on the ones we have and those we don't for each category
        for uid in self.unwanted.lst:
            self.remove(uid, self.unwanted.dic[uid])
        self.new_jar = history.Jar(config.paths, self.sub)
        for uid in self.wanted.lst:
            entry = self.wanted.dic[uid]
            if uid not in self.jar.lst:
                self.get(uid, entry, config.args)
            else:
                self.check(uid, entry, config.args)
            self.new_jar.lst.append(uid)
            self.new_jar.dic[uid] = entry
            self.new_jar.save()
        # should any by mistake remain in the old jar (i.e. not have been 
        # either removed or renewed) we add them to the new jar. 
        for uid in self.jar.lst:
            self.check(uid, self.jar.dic[uid], config.args)
        logger.info('')

    def remove(self, uid, entry):
        self.logger.info(' Removing existing file:  ' + entry['poca_filename'])
        # first we delete the actual file
        files.delete_file(entry['poca_abspath'])
        # then remove the entry from the jar list and dictionary
        self.jar.lst.remove(uid)
        dummy = self.jar.dic.pop(uid)
        self.jar.save()

    def get(self, uid, entry, args):
        files.download_audio_file(args, entry)

    def check(self, uid, entry, args):
        self.logger.info(' Checking existing file:  ' + entry['poca_filename'])
        if not path.isfile(entry['poca_abspath']):
            self.get(uid, args)
        self.jar.lst.remove(uid)
        dummy = self.jar.dic.pop(uid)

class Feed:
    def __init__(self, sub):
        doc = feedparser.parse(sub.url)
        self.lst = [ entry.id for entry in doc.entries ]
        self.dic = { entry.id : entry for entry in doc.entries }

class Combo:
    def __init__(self, feed, jar):
        '''Copies feed then adds non-duplicates from jar'''
        self.lst = list(feed.lst)
        self.lst.extend(x for x in jar.lst if x not in feed.lst)
        self.dic = feed.dic.copy()
        self.dic.update(jar.dic)

class Wanted():
    def __init__(self, sub, combo, logger):
        self.lst, self.dic = ( [], {} )
        mega = float(1024 * 1024)
        self.max_bytes = int(sub.max_mb) * mega
        self.cur_bytes = 0

        for uid in combo.lst:
            entry = combo.dic[uid]
            uid_bytes = self.get_size(entry)
            if self.cur_bytes + uid_bytes < self.max_bytes:
                self.cur_bytes += uid_bytes
                self.lst.append(uid)
                entry['poca_url'] = entry.enclosures[0]['href']
                entry['poca_size'] = uid_bytes
                entry['poca_filename'] = self.get_filename(entry)
                entry['poca_abspath'] = path.join(sub.sub_dir, entry['poca_filename'])
                self.dic[uid] = entry
                logger.info(' Adding to wanted list:   ' + entry.title + 
                    ' @ ' + str(round(uid_bytes / mega, 2)) + ' Mb')
            else:
                break
        logger.info(' Total size:              ' + 
            str(round(self.cur_bytes / mega, 2)) + ' / ' + 
            str(round(self.max_bytes / mega, 2)) + ' Mb')

    def get_size(self, entry):
        try:
            size = int(entry.enclosures[0]['length'])
        except KeyError:
            if entry.has_key('poca_size'):
                size = entry['poca_size']
            else:
                url = entry.enclosures[0]['href'].encode('ascii')
                size = int(self.get_file_info(url, 'Content-Length'))
        return size

    def get_file_info(self, url, info_key):
        '''Gets stats about the file to be downloaded, such as file size'''
        f = urllib2.urlopen(url)
        value = f.info()[info_key]
        f.close()
        return value

    def get_filename(self, entry):
        '''Parses URL to find base filename'''
        parsed_url = urlparse(entry['poca_url'])
        filename = path.basename(parsed_url.path)
        return filename

class Unwanted:
    def __init__(self, jar, wanted):
        self.lst = [ uid for uid in jar.lst if uid not in wanted.lst ]
        self.dic = { uid : jar.dic[uid] for uid in self.lst }

