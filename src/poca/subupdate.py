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
from copy import deepcopy
from threading import Thread

import feedparser
from lxml import etree
from poca import files, history, entryinfo
from poca.lxmlfuncs import merge
from poca.outcome import Outcome


class SubUpdateThread(Thread):
    '''A thread class that creates a SubData instance and puts it in the
       queue'''
    def __init__(self, queue, target, *args):
        self.queue = queue
        self.target = target
        self.args = args
        super(SubUpdateThread, self).__init__()
        self.daemon = True

    def run(self):
        subdata = self.target(*self.args)
        self.queue.put(subdata)


class SubUpdate():
    '''Data carrier for subscription: entries to dl, entries to remove,
       user deleted entries, etc.'''
    def __init__(self, conf, sub):
        self.conf = conf
        self.sub = sub
        self.status = 0
        self.sub_dir = os.path.join(self.conf.xml.settings.base_dir.text,
                                    self.sub.title.text)
        self.outcome = files.check_path(self.sub_dir)
        if not self.outcome.success:
            return

        # merge sub settings and defaults
        defaults = deepcopy(self.conf.xml.defaults)
        rename = deepcopy(self.sub.rename) if hasattr(self.sub, 'rename') \
            else None
        errors = merge(self.sub, defaults, self.conf.xml.defaults, errors=[])
        self.outcome = errors[0] if errors else Outcome(True, '')
        defaults.tag = "subscription"
        self.sub = defaults
        if rename is not None:
            self.sub.rename = rename
        if not self.outcome.success:
            return

        # get jar and check for user deleted files
        self.udeleted = []
        self.jar, self.outcome = history.get_subjar(self.conf.paths,
                                                    self.sub)
        if not self.outcome.success:
            return
        self.check_jar()
        if not self.outcome.success:
            return

        # get feed, combine with jar and filter the lot
        feed = Feed(self.sub, self.jar, self.udeleted)
        self.status = feed.status
        if self.status == 301:
            self.outcome = Outcome(True, 'Feed has moved. Config updated.')
            self.new_url = feed.href
        elif self.status == 304:
            self.outcome = Outcome(True, 'Not modified')
            return
        elif self.status >= 400:
            self.outcome = Outcome(False, feed.bozo_exception)
            return
        else:
            self.outcome = Outcome(True, 'Success')
        combo = Combo(feed, self.jar, self.sub)
        self.wanted = Wanted(self.sub, feed, combo, self.jar.del_lst,
                             self.sub_dir)
        self.outcome = self.wanted.outcome
        if not self.outcome.success:
            return
        from_the_top = self.sub.find('from_the_top') or 'no'
        if from_the_top == 'no':
            self.wanted.lst.reverse()

        # subupgrade will delete unwanted and download lacking
        self.unwanted = [x for x in self.jar.lst if x not in self.wanted.lst]
        self.lacking = [x for x in self.wanted.lst if x not in self.jar.lst]

    def check_jar(self):
        '''Check for user deleted files so we can filter them out'''
        for uid in self.jar.lst:
            entry = self.jar.dic[uid]
            outcome = files.verify_file(entry)
            if not outcome.success:
                self.udeleted.append(entry)
                self.jar.del_lst.append(uid)
                self.jar.del_dic[uid] = self.jar.dic.pop(uid)
        self.jar.lst = [x for x in self.jar.lst if x not in self.jar.del_lst]
        self.outcome = self.jar.save()


class Feed:
    '''Constructs a container for feed entries'''
    def __init__(self, sub, jar, udeleted):
        etag = getattr(jar, 'etag', None)
        modified = getattr(jar, 'modified', None)
        sub_str = etree.tostring(sub, encoding='unicode')
        jarsub_str = etree.tostring(jar.sub, encoding='unicode')
        if sub_str != jarsub_str or udeleted:
            etag = None
            modified = None
        doc = feedparser.parse(sub.url.text, etag=etag, modified=modified)
        self.status = getattr(doc, 'status', 418)
        self.etag = getattr(doc, 'etag', etag)
        self.modified = getattr(doc, 'modified', modified)
        self.bozo_exception = getattr(doc, 'bozo_exception', str())
        self.href = getattr(doc, 'href', sub.url.text)
        self.set_entries(doc, sub)

    def set_entries(self, doc, sub):
        '''Extract entries from the feed xml'''
        try:
            self.lst = [entry.id for entry in doc.entries]
            self.dic = {entry.id: entry for entry in doc.entries}
        except (KeyError, AttributeError):
            try:
                self.lst = [entry.enclosures[0]['href']
                            for entry in doc.entries]
                self.dic = {entry.enclosures[0]['href']: entry
                            for entry in doc.entries}
            except (KeyError, AttributeError):
                self.outcome = Outcome(False, 'Cant find entries in feed.')
                # should we set an artificial status here? Or does feedparser?
                # return
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
    def __init__(self, feed, jar, sub):
        from_the_top = sub.find('from_the_top') or 'no'
        if from_the_top == 'yes':
            self.lst = list(jar.lst)
            self.lst.extend(uid for uid in feed.lst if uid not in jar.lst)
        else:
            self.lst = list(feed.lst)
            self.lst.extend(uid for uid in jar.lst if uid not in feed.lst)
        self.dic = {uid: entryinfo.validate(feed.dic[uid]) for uid in feed.lst
                    if uid not in jar.lst}
        self.dic.update(jar.dic)


class Wanted():
    '''Filters the combo entries and decides which ones to go for'''
    def __init__(self, sub, feed, combo, del_lst, sub_dir):
        self.outcome = Outcome(True, 'Wanted entries assembled')
        self.lst = combo.lst
        self.lst = list(filter(lambda x: x not in del_lst, self.lst))
        self.lst = list(filter(lambda x: combo.dic[x]['valid'], self.lst))
        if hasattr(sub, 'filters'):
            self.apply_filters(sub, combo)
        if hasattr(sub, 'max_number'):
            self.limit(sub)
        self.dic = {uid: entryinfo.expand(combo.dic[uid], sub, sub_dir)
                    for uid in self.lst}
        filename_set = {self.dic[uid]['poca_filename'] for uid in self.lst}
        if len(filename_set) < len(self.lst):
            self.outcome = Outcome(False, "Filename used more than once. "
                                   "Use rename tag to fix.")
        self.feed_etag = feed.etag
        self.feed_modified = feed.modified
        self.feed_image = feed.image

    def match_filename(self, dic, filter_text):
        '''The episode filename must match a regex/string'''
        self.lst = [x for x in self.lst if
                    bool(re.search(filter_text, dic[x]['filename']))]

    def match_title(self, dic, filter_text):
        '''The episode title must match a regex/string'''
        self.lst = [x for x in self.lst if
                    bool(re.search(filter_text, dic[x]['title']))]

    def match_weekdays(self, dic, filter_text):
        '''Only return episodes published on specific week days'''
        self.lst = [x for x in self.lst if
                    str(dic[x]['published_parsed'].tm_wday) in
                    list(filter_text)]

    def match_date(self, dic, filter_text):
        '''Only return episodes published after a specific date'''
        filter_date = time.strptime(filter_text, '%Y-%m-%d')
        self.lst = [x for x in self.lst if dic[x]['published_parsed'] >
                    filter_date]

    def match_hour(self, dic, filter_text):
        '''Only return episodes published at a specific hour of the day'''
        self.lst = [x for x in self.lst if dic[x]['published_parsed'].tm_hour
                    == int(filter_text)]

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
            try:
                func_dic[key](combo.dic, sub.filters[key].text)
                self.outcome = Outcome(True, 'Filters applied successfully')
            except KeyError as e:
                self.outcome = Outcome(False, 'Entry is missing info: %s' % e)
            except (ValueError, TypeError, SyntaxError) as e:
                self.outcome = Outcome(False, 'Bad filter setting')

    def limit(self, sub):
        '''Limit the number of episodes to that set in max_number'''
        try:
            self.lst = self.lst[:int(sub.max_number)]
            self.outcome = Outcome(True, 'Number limited successfully')
        except ValueError:
            self.outcome = Outcome(False, 'Bad max_number setting')
