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
        '''A class for a single subscription/channel'''
        self.sub = sub
        db_filename = path.join(config.paths.db_dir , self.sub.title)
        # Find all available entries
        self.feed = Feed(self.sub)
        self.jar = history.get_jar(db_filename)
        self.combo = Combo(self.feed, self.jar)
        # Find all the ones we want (and don't want)
        self.wanted = Wanted(self.sub, self.combo)
        self.unwanted = Unwanted(self.jar, self.wanted)
        # Act on the ones we have and those we don't for each category
        for uid in self.unwanted.lst:
            self.remove(uid)
        self.new_jar = history.Jar(db_filename)
        files.check_path(self.sub)
        for uid in self.wanted.lst:
            if uid not in self.jar.lst:
                self.get(config.args, uid)
            else:
                self.check(uid)

    def remove(self, uid):
        print 'removing ', uid
        entry = self.unwanted.dic[uid]
        files.delete_audio_file(entry)
        #consider removing it from self.jar at this stage and updating the file

    def get(self, args, uid):
        entry = self.wanted.dic[uid]
        files.download_audio_file(args, entry)
        self.new_jar.lst.append(uid)
        self.new_jar.dic[uid] = entry
        self.new_jar.save()

    def check(self, uid):
        title = self.wanted.dic[uid]['poca_filename']
        print 'Checking existing file: ', title

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
    def __init__(self, sub, combo):
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
                print 'Adding to wanted list: ', entry.title, ' @ ', round(uid_bytes / mega, 2), ' Mb'
            else:
                break

        print 'Total size: ', round(self.cur_bytes / mega, 2), ' out of ', round(self.max_bytes / mega, 2), ' Mb'

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
        '''why is this a function of its own?'''
        return path.basename(entry['poca_url'])

class Unwanted:
    def __init__(self, jar, wanted):
        self.lst = [ uid for uid in jar.lst if uid not in wanted.lst ]
        self.dic = { uid : jar.dic[uid] for uid in self.lst }

class oldChannel:
    def __init__(self, sub_dic, sub_log):
        '''A class for a single subscription/channel. It will parse the feed, \
        and create and maintain a data structure to be used for determining \
        files to download and delete etc.'''
        self.sub_dic = sub_dic
        self.entry_db = {}
        self.entries = {'green': [], 'yellow': [], 'red': []}
        self.reconfigure = False
        self.updated = None
        if sub_log:
            self.entries.update(sub_log['entries'])
            self.entry_db = sub_log['entry_db']
            self.updated = sub_log['updated']
            if sub_log['max_mb'] != int(sub_dic['max_mb']):
                self.reconfigure = True
        print self.entries
        print self.entry_db


    def parse_feed(self):
        '''Uses Mark Pilgrims feedparser module to download and parse. If the \
        entry is unknown, its data is added to the green list.'''
        self.doc = feedparser.parse(self.sub_dic['url'])
        if self.doc.bozo and not self.doc.entries:
            error = "Feed could not be parsed. "
            suggest = ["Please check your connection, URL, and feed file,", \
            "in that order."]
            errors.errors(error, suggest, fatal=False, title=self.sub_dic['title'].upper())
            return False
        try:
            if self.doc['updated'] == self.updated:
                return False
            else:
                self.updated = self.doc['updated']
        except KeyError:
            pass
        return True

    def find_new(self):
        self.entries['oranges'] = []
        for entry in self.doc['entries']:
            if entry.id in self.entries['yellow']:
                continue
            if entry.id in self.entries['red']:
                self.entries['oranges'].append(entry.id)
                continue
            entry_dic = {}
            entry_dic['title'] = entry.title
            entry_dic['pubdate'] = entry.updated
            entry_dic['url'] = entry.enclosures[0]['href'].encode('ascii')
            try:
                entry_dic['filename'] = self._get_filename(entry_dic)
            except urllib2.HTTPError:
                continue
            try:
                entry_dic['length'] = int(entry.enclosures[0]['length'])
            except (ValueError, KeyError):
                entry_dic['length'] = int(self._get_file_info(entry_dic, \
                'Content-Length'))
            self.entries['green'].append(entry.id)
            self.entry_db[entry.id] = entry_dic
        return True

    def find_old(self):
        red_set = set(self.entries['red'])
        orange_set = set(self.entries['oranges'])
        for entry in red_set.difference(orange_set):
            self.entries['red'].remove(entry)
            del(self.entry_db[entry])
            # print entry

    def analyze_for_size(self):
        '''Analyzes the available sound files, i.e. those currently in folder \
        (yellow) plus new ones available for download (green), to find which \
        ones make the cut (limes).'''
        self.entries['lemons'] = self.entries['green'] + self.entries['yellow']
        self.entries['limes'] = list(self.entries['lemons'])
        if self.reconfigure:
            self.entries['limes'] += self.entries['red']
        byte_count = 0
        for entry in self.entries['limes']:
            byte_count += self.entry_db[entry]['length']
        while byte_count > self.sub_dic['max_bytes']:
            entry = self.entries['limes'].pop()
            byte_count -= self.entry_db[entry]['length']

    def create_change_lists(self):
        '''Creates lists of files to be deleted (grapefruits), downloaded \
        (pomelos) and passed directly to red because of space limitations \
        (citrons).'''
        self.entries['pomelos'] = list(self.entries['limes'])
        for entry in self.entries['yellow']:
            if entry in self.entries['pomelos']:
                self.entries['pomelos'].remove(entry)
        self.entries['grapefruits'] = list(self.entries['yellow'])
        for entry in self.entries['limes']:
            if entry in self.entries['grapefruits']:
                self.entries['grapefruits'].remove(entry)
        self.entries['citrons'] = list(self.entries['green'])
        if self.reconfigure:
            for entry in self.entries['pomelos']:
                if entry in self.entries['red']:
                    self.entries['red'].remove(entry)                    
                    self.entries['citrons'].append(entry)                    
        for entry in self.entries['pomelos']:
            self.entries['citrons'].remove(entry)

    def new_history_dic(self):
        '''Saves new lists - new red is old red plus old downloads to be \
        deleted plus new entries for which there arent room. New yellow is \
        limes, i.e. the set of entries for which there is room.'''
        new_red = self.entries['citrons'] + self.entries['grapefruits'] + \
            self.entries['red']
        new_yellow = self.entries['limes']
        new_entries = {'red': new_red, 'yellow': new_yellow}
        return {'entries': new_entries, \
        'entry_db': self.entry_db, \
        'max_mb': int(self.sub_dic['max_mb']), \
        'updated': self.updated}

    def _get_filename(self, entry_dic):
        '''Checks for file existence and redirects and \
        removes query strings from url.'''
        f = urllib2.urlopen(entry_dic['url'])
        parsed_url = urlparse(f.geturl())
        filename = path.basename(parsed_url.path)
        f.close()
        return filename

