# Copyright 2010, 2011, 2015 Mads Michelsen (reannual@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.


import logging
import urllib2
from os.path import basename 
from urlparse import urlparse

import feedparser

from poco import errors


class Channel:
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
        filename = basename(parsed_url.path)
        f.close()
        return filename

    def _get_file_info(self, entry_dic, info_key):
        '''Gets stats about the file to be downloaded, such as file size'''
        f = urllib2.urlopen(entry_dic['url'])
        value = f.info()[info_key]
        f.close()
        return value
        
            
        
