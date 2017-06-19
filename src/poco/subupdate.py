# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Update feed in thread"""

import os
import re
import time

from threading import Thread
from copy import deepcopy

import feedparser

from poco import files, history, entryinfo, output
from poco.outcome import Outcome
from poco.config import merge


class SubThread(Thread):
    '''A thread class that creates a SubData instance and puts it in the
       queue'''
    def __init__(self, queue, target, *args):
        self.queue = queue
        self._target = target
        self._args = args
        super(SubThread, self).__init__()

    def run(self):
        subdata = self._target(self._args)
        self.queue.put(subdata)


class SubData():
    '''Data carrier for subscription: entries to dl, entries to remove,
       user deleted entries, etc.'''
    def __init__(self, conf, sub):
        # basic sub set up and prerequisites
        self.conf = conf
        self.sub = sub
        self.outcome = Outcome(True, '')
        self.ctitle = self.sub.title.text.upper()
        self.sub_dir = os.path.join(self.conf.xml.settings.base_dir.text,
                                    self.sub.title.text)
        self.outcome = files.check_path(self.sub_dir)
        if not self.outcome.success:
            return

        # merge sub settings and defaults
        defaults = deepcopy(self.conf.xml.defaults)
        errors = merge(self.sub, defaults, self.conf.xml.defaults, errors=[])
        self.outcome = errors[0] if errors else Outcome(True, '')
        defaults.tag = "subscription"
        self.sub = defaults
        if not self.outcome.success:
            return

        # get jar and check for user deleted files
        self.udeleted = []
        self.jar, self.outcome = history.get_subjar(self.conf.paths,
                                                    self.sub)
        if not self.outcome.success:
            return
        self.check_jar()

        # get feed, combine with jar and filter the lot
        feed = Feed(self.sub, self.jar, self.udeleted)
        self.outcome = feed.outcome
        if not self.outcome.success:
            return
        combo = Combo(feed, self.jar, self.sub, self.sub_dir)
        self.wanted = Wanted(self.sub, feed, combo, self.jar.del_lst)
        from_the_top = self.sub.find('from_the_top') or 'no'
        if from_the_top == 'no':
            self.wanted.lst.reverse()

        # inform user of intentions
        self.unwanted = [x for x in self.jar.lst if x not in self.wanted.lst]
        self.lacking = [x for x in self.wanted.lst if x not in self.jar.lst]
        #self.unwanted = set(self.jar.lst) - set(self.wanted.lst)
        #self.lacking = set(self.wanted.lst) - set(self.jar.lst)
        #output.plans(self.ctitle, len(self.udeleted), len(self.unwanted),
        #             len(self.lacking))

    def check_jar(self):
        '''Check for user deleted files so we can filter them out'''
        for uid in self.jar.lst:
            entry = self.jar.dic[uid]
            outcome = files.verify_file(entry)
            if not outcome.success:
                self.udeleted.append(entry)
                self.jar.del_lst.append(uid)
                self.jar.del_dic[uid] = self.jar.dic.pop(uid)
        # we change the list after the loop because we don't want to saw the
        # branch we're sitting on. but maybe it would be smarter to just loop
        # a copy and pop the lst entries into del_lst?
        self.jar.lst = [x for x in self.jar.lst if x not in self.jar.del_lst]
        self.jar.save()
        # currently no jar-save checks

class Feed:
    '''Constructs a container for feed entries'''
    def __init__(self, sub, jar, udeleted):
        self.outcome = Outcome(True, '')
        self.etag = jar.etag
        # does comapring sub instances actually work?
        # does it ever see that sub_a is the same as sub_b?
        if sub != jar.sub or udeleted:
            self.etag = None
        doc = self.update(sub)
        self.set_entries(doc, sub)

    def update(self, sub):
        '''Check feed, return the xml'''
        doc = feedparser.parse(sub.url.text, etag=self.etag)
        # save new etag if there is one in doc
        if doc.has_key('etag'):
            self.etag = doc.etag
        # only bozo for actual errors
        if doc.bozo and not doc.entries:
            if 'status' in doc:
                # if etag is 304 doc.entries is empty and we proceed as normal
                if doc.status != 304:
                    self.outcome = Outcome(False, str(doc.bozo_exception))
            else:
                self.outcome = Outcome(False, str(doc.bozo_exception))
        return doc

    def set_entries(self, doc, sub):
        '''Extract entries from the feed xml'''
        try:
            self.lst = [entry.id for entry in doc.entries]
            self.dic = {entry.id : entry for entry in doc.entries}
        except (KeyError, AttributeError):
            try:
                self.lst = [entry.enclosures[0]['href']
                            for entry in doc.entries]
                self.dic = {entry.enclosures[0]['href'] : entry
                            for entry in doc.entries}
            except (KeyError, AttributeError):
                self.outcome = Outcome(False, 'Cant find entries in feed.')
        from_the_top = sub.find('from_the_top') or 'no'
        if from_the_top == 'yes':
            self.lst.reverse()
        try:
            self.image = doc.feed.image['href']
        except (AttributeError, KeyError):
            self.image = None

class Combo:
    '''Constructs a container holding all combined feed and jar
    entries. Copies feed then adds non-duplicates from jar'''
    def __init__(self, feed, jar, sub, sub_dir):
        from_the_top = sub.find('from_the_top') or 'no'
        if from_the_top == 'yes':
            self.lst = list(jar.lst)
            self.lst.extend(uid for uid in feed.lst if uid not in jar.lst)
        else:
            self.lst = list(feed.lst)
            self.lst.extend(uid for uid in jar.lst if uid not in feed.lst)
        self.dic = {uid: entryinfo.expand(feed.dic[uid], sub, sub_dir)
                    for uid in feed.lst if uid not in jar.lst}
        self.dic.update(jar.dic)

class Wanted():
    '''Filters the combo entries and decides which ones to go for'''
    def __init__(self, sub, feed, combo, del_lst):
        self.lst = combo.lst
        self.lst = list(filter(lambda x: x not in del_lst, self.lst))
        self.lst = list(filter(lambda x: combo.dic[x]['valid'], self.lst))
        if hasattr(sub, 'filters'):
            self.apply_filters(sub, combo)
        # we don't know that max_number is a number
        if hasattr(sub, 'max_number'):
            self.limit(sub)
        self.dic = {x: combo.dic[x] for x in self.lst}
        self.feed_etag = feed.etag
        self.feed_image = feed.image

    def match_filename(self, dic, filter_text):
        '''The episode filename must match a regex/string'''
        self.lst = [x for x in self.lst if
                    bool(re.search(filter_text, dic[x]['poca_filename']))]

    def match_title(self, dic, filter_text):
        '''The episode title must match a regex/string'''
        self.lst = [x for x in self.lst if
                    bool(re.search(filter_text, dic[x]['title']))]

    def match_weekdays(self, dic, filter_text):
        '''Only return episodes published on specific week days'''
        self.lst = [x for x in self.lst if
                    str(dic[x]['updated_parsed'].tm_wday) in list(filter_text)]

    def match_date(self, dic, filter_text):
        '''Only return episodes published after a specific date'''
        filter_date = time.strptime(filter_text, '%Y-%m-%d')
        self.lst = [x for x in self.lst if dic[x]['published_parsed'] >
                    filter_date]

    def match_hour(self, dic, filter_text):
        '''Only return episodes published at a specific hour of the day'''
        self.lst = [x for x in self.lst if dic[x]['updated_parsed'].tm_hour ==
                    int(filter_text)]

    def apply_filters(self, sub, combo):
        '''Apply all filters set to be used on the subscription'''
        func_dic = {'after_date': self.match_date,
                    'filename': self.match_filename,
                    'title': self.match_title,
                    'hour': self.match_hour,
                    'weekdays': self.match_weekdays}
        filters = {node.tag for node in sub.filters.iterchildren()}
        valid_filters = filters & set(func_dic.keys())
        for key in valid_filters:
            func_dic[key](combo.dic, sub.filters[key].text)

    def limit(self, sub):
        '''Limit the number of episodes to that set in max_number'''
        self.lst = self.lst[:int(sub.max_number)]
