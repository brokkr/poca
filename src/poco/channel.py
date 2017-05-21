# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Per-subscription operations"""

import os
import re
import sys
import time
from copy import deepcopy

import feedparser

from poco import files, history, entryinfo, output, tag
from poco.outcome import Outcome


class Channel:
    '''A class for a single subscription/channel. Creates the containers
    first, then acts on them and updates the db as it goes.'''
    def __init__(self, config, sub):
        self.config = config
        defaults = deepcopy(config.defaults)
        self.extend(sub, defaults)
        for element in defaults.xpath('./metadata|./filters'):
            self.extend(sub[element.tag], element)
        self.sub = sub
        self.sub_dir = os.path.join(config.settings.base_dir.text,
                                    self.sub.title.text)
        self.ctitle = self.sub.title.text.upper()
        self.outcome = Outcome(True, '')

    def extend(self, base, extension):
        '''extend lxml objectify subelements'''
        base_set = {el.tag for el in base.iterchildren()}
        extend_set = {el.tag for el in extension.iterchildren()}
        additions = extend_set.difference(base_set)
        base.extend([extension[el_tag] for el_tag in additions])

    def make_plans(self):
        '''Calculate what files to get and what files to dump'''
        # see that we can write to the designated directory
        self.outcome = files.check_path(self.sub_dir)
        if not self.outcome.success:
            output.suberror(self.ctitle, outcome)
            return

        # get jar and check for user deleted files
        self.udeleted = []
        self.jar, self.outcome = history.get_subjar(self.config.paths,
                                                    self.sub)
        if not self.outcome.success:
            output.suberror(self.ctitle, outcome)
            return
        self.check_jar()

        # get feed, combine with jar and filter the lot
        self.feed = Feed(self.sub, self.jar, self.udeleted)
        self.outcome = self.feed.outcome
        if not self.outcome.success:
            output.suberror(self.ctitle, self.outcome)
            return
        self.combo = Combo(self.feed, self.jar, self.sub, self.sub_dir)
        self.wanted = Wanted(self.sub, self.combo, self.jar.del_lst)

        # inform user of intentions
        self.unwanted = set(self.jar.lst) - set(self.wanted.lst)
        self.lacking = set(self.wanted.lst) - set(self.jar.lst)
        output.plans(self.ctitle, len(self.udeleted), len(self.unwanted),
                     len(self.lacking))
        self.removed, self.downed, self.failed = [], [], []

    def follow_through(self):
        '''Act on the plans laid out'''
        # loop through user deleted and indicate recognition
        for entry in self.udeleted:
            output.notice_udeleted(entry)

        # loop through unwanted (set) entries to remove
        for uid in self.unwanted:
            entry = self.jar.dic[uid]
            self.remove(uid, entry)
            if not self.outcome.success:
                output.suberror(self.ctitle, self.outcome)
                return

        # loop through wanted (list) entries to acquire
        for uid in self.wanted.lst:
            if uid not in self.lacking:
                continue
            entry = self.wanted.dic[uid]
            self.acquire(uid, entry)

        # save etag and subsettings after succesful update
        if not self.failed:
            self.jar.sub = self.sub
            self.jar.etag = self.feed.etag
        self.jar.save()

        # download cover image
        if self.downed and self.feed.image:
            outcome = files.download_img_file(self.feed.image, self.sub_dir,
                                              self.config.settings)

        # print summary of operations in file log
        output.summary(self.ctitle, self.udeleted, self.removed,
                       self.downed, self.failed)


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
        self.jar.save()
        # currently no jar-save checks

    def acquire(self, uid, entry):
        '''Get new entries, tag them and add to history'''
        # see https://github.com/brokkr/poca/wiki/Architecture#wantedindex
        output.downloading(entry)
        wantedindex = self.wanted.lst.index(uid) - len(self.failed)
        outcome = files.download_file(entry['poca_url'],
                                      entry['poca_abspath'], self.config.settings)
        if outcome.success:
            outcome = tag.tag_audio_file(self.config.settings, self.sub, entry)
            if not outcome.success:
                output.tag_fail(outcome)
                # add to failed?
            self.add_to_jar(uid, entry, wantedindex)
            self.downed.append(entry)
        else:
            output.dl_fail(outcome)
            self.failed.append(entry)

    def add_to_jar(self, uid, entry, wantedindex):
        '''Add new entry to jar'''
        self.jar.lst.insert(wantedindex, uid)
        self.jar.dic[uid] = entry
        self.outcome = self.jar.save()
        # currently no jar-save checks

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the jar'''
        output.removing(entry)
        self.outcome = files.delete_file(entry['poca_abspath'])
        if not self.outcome.success:
            return
        self.jar.lst.remove(uid)
        del(self.jar.dic[uid])
        self.outcome = self.jar.save()
        # currently no jar-save checks
        self.removed.append(entry)

class Feed:
    '''Constructs a container for feed entries'''
    def __init__(self, sub, jar, udeleted):
        self.outcome = Outcome(True, '')
        self.etag = jar.etag
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
    def __init__(self, sub, combo, del_lst):
        self.lst = combo.lst
        self.lst = list(filter(lambda x: x not in del_lst, self.lst))
        self.lst = list(filter(lambda x: combo.dic[x]['valid'], self.lst))
        if hasattr(sub, 'filters'):
            self.apply_filters(sub, combo)
        # we don't know that max_number is a number
        if hasattr(sub, 'max_number'):
            self.limit(sub)
        self.dic = {x: combo.dic[x] for x in self.lst}

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
        for key in sub.filters.iterchildren():
            func_dic[key.tag](combo.dic, key.text)

    def limit(self, sub):
        '''Limit the number of episodes to that set in max_number'''
        self.lst = self.lst[:int(sub.max_number)]
