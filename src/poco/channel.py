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
    def __init__(self, config, logger, sub):
        '''A class for a single subscription/channel. Creates the containers
        first, then acts on them and updates the db as it goes.'''
        self.sub, self.logger = sub, logger
        self.logger.info(sub.title.upper())

        self.feed = Feed(self.sub)
        self.jar = history.get_jar(config.paths, self.sub)
        self.combo = Combo(self.feed, self.jar)
        self.wanted = Wanted(self.sub, self.combo, logger)

        for uid in list(set(self.jar.lst) - set(self.wanted.lst)):
            self.remove(uid, self.jar.dic[uid])
            # insert return value to see if removal was successful
        self.new_jar = history.Jar(config.paths, self.sub)
        for uid in self.wanted.lst:
            entry = self.wanted.dic[uid]
            # insert return value to see if download/check was successful
            if uid not in self.jar.lst:
                files.download_audio_file(config.args, entry)
            else:
                self.check(uid, entry, config.args)
            self.new_jar.lst.append(uid)
            self.new_jar.dic[uid] = entry
            self.new_jar.save()
        # should any - by mistake - remain in the old jar (i.e. not have been 
        # either removed or renewed) we add them to the new jar. 
        for uid in self.jar.lst:
            self.check(uid, self.jar.dic[uid], config.args)
        logger.info('')

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the old jar'''
        self.logger.info(' Removing existing file:  ' + entry['poca_filename'])
        files.delete_file(entry['poca_abspath'])
        self.jar.lst.remove(uid)
        dummy = self.jar.dic.pop(uid)
        self.jar.save()
        # return something something

    def check(self, uid, entry, args):
        '''Performs a quick check-up on existing keeper-files and removes 
        the entry from the old jar'''
        self.logger.info(' Checking existing file:  ' + entry['poca_filename'])
        if not path.isfile(entry['poca_abspath']):
            files.download_audio_file(args, entry)
        self.jar.lst.remove(uid)
        dummy = self.jar.dic.pop(uid)
        # return something something

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
        mega = float(1024 * 1024)
        self.max_bytes = int(sub.max_mb) * mega
        self.cur_bytes = 0

        for uid in combo.lst:
            entry = combo.dic[uid]
            entry['poca_url'] = entry.enclosures[0]['href']
            entry['poca_size'] = self.get_size(entry)
            entry['poca_filename'] = self.get_filename(entry)
            entry['poca_abspath'] = path.join(sub.sub_dir, 
                entry['poca_filename'])
            if self.cur_bytes + entry['poca_size'] < self.max_bytes:
                self.cur_bytes += entry['poca_size']
                self.lst.append(uid)
                self.dic[uid] = entry
                logger.info(' Adding to wanted list:   ' + entry.title + 
                    ' @ ' + str(round(uid_bytes / mega, 2)) + ' Mb')
            else:
                break
        logger.info(' Total size:              ' + 
            str(round(self.cur_bytes / mega, 2)) + ' / ' + 
            str(round(self.max_bytes / mega, 2)) + ' Mb')

    def get_size(self, entry):
        '''Returns the entrys size in bytes. Tries to get if off of the
        enclosure, otherwise pokes url for info.'''
        try:
            size = int(entry.enclosures[0]['length'])
        except KeyError:
            size = int(self.get_file_info(entry['poca_url'], 'Content-Length'))
        return size

    def get_file_info(self, url, info_key):
        '''Gets stats about the file to be downloaded, such as file size'''
        # Maybe integrte into get_size seeing as it's the only one to make 
        # use of it? what other file info can we imagine having a use for?
        f = urllib2.urlopen(url)
        value = f.info()[info_key]
        f.close()
        return value

    def get_filename(self, entry):
        '''Parses URL to find base filename. To be expanded with naming
        options'''
        parsed_url = urlparse(entry['poca_url'])
        filename = path.basename(parsed_url.path)
        return filename

