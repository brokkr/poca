#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Feed stats"""


import time
import feedparser


empty_entry = {'title': 'n/a', 'published_parsed': None}


class Feedstats():
    '''Gathers stats for feed and arranges output'''
    def __init__(self, url):
        '''Publishing stats on an RSRSS feed'''
        self.url = url
        self.doc = feedparser.parse(self.url)
        now = time.localtime()
        self.entries = [entry for entry in self.doc.entries if
                        self.age(now, entry['published_parsed']) < 35]

    def age(self, now, date):
        try:
            days = (time.mktime(now) - time.mktime(date)) / (24*3600)
        except TypeError:
            days = 100
        return round(days)

    def print_stats(self):
        '''Output the lef hand and right hand side of the matrix'''
        self.set_lhs()
        self.set_rhs()
        for index in range(8):
            print(self.lhs_lst[index] + self.rhs_lst[index])

    def set_lhs(self):
        '''Collect feedinfo and arrange the lhs'''
        lhs = {}
        lhs['author'] = self.doc.feed.author if 'author' in self.doc.feed \
            else 'Unknown'
        lhs['title'] = self.doc.feed.title if 'title' in self.doc.feed else \
            'Unknown'
        last = self.doc.entries[0] if self.doc.entries else empty_entry
        try:
            lhs['last_date'] = time.strftime('%d %b %Y',
                                             last['published_parsed'])
        except TypeError:
            lhs['last_date'] = 'n/a'
        lhs['last_title'] = str(last['title']) if 'title' in last else 'n/a'
        lhs['avg_mb'] = self.get_avg_size()
        lhs['avg_duration'] = self.get_avg_duration()
        headers = {'author': 'Author: ', 'title': 'Title:  ',
                   'last_date': 'Published:    ',
                   'last_title': 'Last episode: ',
                   'avg_duration': 'Avg. length of episode: ',
                   'avg_mb': 'Avg. size of episode:   '}
        order = ['author', 'title', 'last_title', 'last_date', 'avg_mb',
                 'avg_duration']
        head_info = lambda x: (headers[x] + lhs[x])[:58].ljust(60)
        self.lhs_lst = [head_info(x) for x in order]
        self.lhs_lst.insert(4, ''.ljust(60))
        self.lhs_lst.insert(2, ''.ljust(60))
        self.author = lhs['author']
        self.title = lhs['title']

    def get_avg_size(self):
        '''Average size in Mb of an episode in the feed'''
        links = [entry['links'] for entry in self.doc.entries]
        lengths = [enc['length'] for sublist in links for enc in sublist
                   if 'length' in enc]
        lengths = [int(x) for x in lengths if int(x) > 0]
        if not lengths:
            return "n/a"
        avg_bytes = sum(lengths)/len(lengths)
        avg_mb = "%s Mb" % int(round(avg_bytes / (1024*1024), 0))
        return avg_mb

    def get_avg_duration(self):
        '''Average duration in hours and minutes of an episode in the feed'''
        duration_entries = [entry for entry in self.doc.entries if
                            'itunes_duration' in entry]
        durations = list(map(self.itunes2seconds, duration_entries))
        durations = [entry for entry in durations if entry > 0]
        if not durations:
            return "n/a"
        avg_seconds = int(sum(durations) / len(durations))
        m, s = divmod(avg_seconds, 60)
        h, m = divmod(m, 60)
        avg_duration = "%sh " % h if h > 0 else ""
        avg_duration += "%sm" % m
        return avg_duration

    def itunes2seconds(self, entry):
        '''Transform itunes_duration string to duration in seconds'''
        itunes_hms = entry['itunes_duration'].split(':')
        itunes_hms.reverse()
        seconds = 0
        for index, number in enumerate(itunes_hms):
            try:
                seconds += pow(60, index) * int(number)
            except ValueError:
                pass
        return int(seconds)

    def set_rhs(self):
        '''Collect feedinfo and arrange the rhs'''
        wdays = [x['published_parsed'].tm_wday for x in self.entries]
        wday_count = {x: 0 for x in range(7)}
        wday_count.update({x: wdays.count(x) for x in set(wdays)})
        self.rhs_lst = ["PUBLISHED / 5 WEEKS", "".ljust(19)]
        for i in reversed(range(5)):
            line = ['▮' if wday_count[x] > i else ' ' for x in range(7)]
            self.rhs_lst.append('  '.join(line))
        self.rhs_lst.append('M  T  W  T  F  S  S')
