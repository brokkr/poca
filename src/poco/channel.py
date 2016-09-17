# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import re
import sys

import feedparser

from poco import files, history, entryinfo, output, tag
from poco.outcome import Outcome


class Channel:
    def __init__(self, config, sub):
        '''A class for a single subscription/channel. Creates the containers
        first, then acts on them and updates the db as it goes.'''
        
        self.sub = sub
        self.title = sub.title.upper()
        self.config = config
        self.udeleted = []

        ### PART 1: PLANS

        # see that we can write to the designated directory
        outcome = files.check_path(sub.sub_dir)
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()

        # get jar and check for user deleted files
        self.jar, outcome = history.get_jar(config.paths, self.sub)
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()
        self.check_jar()

        # get feed, combine with jar and filter the lot
        self.feed = Feed(self.sub, self.jar, self.udeleted)
        if not self.feed.outcome.success:
            output.suberror(self.title, self.feed.outcome)
            return 
        self.combo = Combo(self.feed, self.jar, self.sub)
        self.wanted = Wanted(self.sub, self.combo, self.jar.del_lst)

        # inform user of intentions
        self.unwanted = set(self.jar.lst) - set(self.wanted.lst)
        self.lacking = set(self.wanted.lst) - set(self.jar.lst)
        output.plans(self.title, len(self.unwanted), len(self.lacking))
        self.removed, self.downed, self.failed = [], [], []

        ### PART 2: ACTION

        # loop through user deleted and indicate recognition
        for uid in self.udeleted:
            entry = self.jar.del_dic[uid]
            output.notice_udeleted(entry)

        # loop through unwanted (set) entries to remove
        for uid in self.unwanted:
            entry = self.jar.dic[uid]
            self.remove(uid, entry)

        # loop through wanted (list) entries to acquire
        for uid in self.wanted.lst:
            if uid not in self.lacking:
                continue
            entry = self.wanted.dic[uid]
            self.acquire(uid, entry)

        # save etag and max after succesful update
        self.jar.max_no = self.feed.max_no 
        if not self.failed:
            self.jar.etag = self.feed.etag
        self.jar.save()

        # download cover image
        if self.downed and self.feed.image:
            outcome = files.download_img_file(self.feed.image, sub.sub_dir)

        # print summary of operations in file log
        output.summary(self.title, self.udeleted, self.removed, self.downed, 
            self.failed)


    def check_jar(self):
        '''Check for user deleted files and mark any such'''
        for uid in self.jar.lst:
            outcome = files.verify_file(self.jar.dic[uid])
            if not outcome.success:
                self.udeleted.append(uid)
                self.jar.del_lst.append(uid)
                self.jar.del_dic[uid] = self.jar.dic.pop(uid)
        self.jar.lst = [ x for x in self.jar.lst if x not in self.jar.del_lst ]
        self.jar.save()
        # testing
        #for uid in self.jar.del_lst:
        #    print(self.jar.del_dic[uid]['poca_filename'])

    def acquire(self, uid, entry):
        '''Get new entries, tag them and add to history'''
        # loop through wanted entries (list) to download
        # Looping through the lacking entries, we insert them at the
        # index they have in wanted.lst. By the time we get to old ones,
        # they will have the correct index. This has been found to 
        # be preferable to a) starting a new list based on wanted 
        # and b) inserting all new entries at the front.
        output.downloading(entry)
        wantedindex = self.wanted.lst.index(uid) - len(self.failed)
        outcome = files.download_file(entry['poca_url'], entry['poca_abspath'])
        if outcome.success:
            outcome = tag.tag_audio_file(self.config.prefs, self.sub, entry)
            if not outcome.success:
                output.tag_fail(outcome)
            self.add_to_jar(uid, entry, wantedindex)
            self.downed.append(entry['poca_filename'])
        else:
            # if a download fails, len(self.failed) is subtracted
            # from wanted index of following files to keep order
            output.dl_fail(outcome)
            self.failed.append(entry['poca_filename'])

    def add_to_jar(self, uid, entry, wantedindex):
        '''Add new entry to jar'''
        self.jar.lst.insert(wantedindex, uid)
        self.jar.dic[uid] = entry
        outcome = self.jar.save()
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()

    def remove(self, uid, entry):
        '''Deletes the file and removes the entry from the jar'''
        output.removing(entry)
        outcome = files.delete_file(entry['poca_abspath'])
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()
        self.jar.lst.remove(uid)
        del(self.jar.dic[uid])
        outcome = self.jar.save()
        if not outcome.success:
            output.subfatal(self.title, outcome)
            sys.exit()
        self.removed.append(entry['poca_filename'])


class Feed:
    def __init__(self, sub, jar, udeleted):
        '''Constructs a container for feed entries'''
        # do we need an update?
        self.etag = jar.etag
        self.max_no = sub.max_no
        if self.max_no != jar.max_no or udeleted:
            self.etag = None
        try:
            doc = feedparser.parse(sub.url, etag=self.etag)
        except TypeError:
            # https://github.com/kurtmckee/feedparser/issues/30#issuecomment-183714444            
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                doc = feedparser.parse(sub.url, etag=self.etag)
            else:
                raise
        # save new etag if one
        if doc.has_key('etag'):
            self.etag = doc.etag
        # only bozo for actual errors
        if doc.bozo and not doc.entries:
            if 'status' in doc:
                # if etag is 304 doc.entries is empty and we proceed as normal
                if doc.status != 304:
                    self.outcome = Outcome(False, str(doc.bozo_exception))
                    return
            else:
                self.outcome = Outcome(False, str(doc.bozo_exception))
                return
        # harvest the entries
        try:
            self.lst = [ entry.id for entry in doc.entries ]
            self.dic = { entry.id : entry for entry in doc.entries }
        except (KeyError, AttributeError):
            try:
                self.lst = [ entry.enclosures[0]['href'] 
                    for entry in doc.entries ]
                self.dic = { entry.enclosures[0]['href'] : entry 
                    for entry in doc.entries }
            except (KeyError, AttributeError):
                self.outcome = Outcome(False, 'Cant find entries in feed.')
        if hasattr(sub, 'from_the_top'):
            self.lst.reverse()
        try:
            self.image = doc.feed.image['href']
        except (AttributeError, KeyError):
            self.image = None
        self.outcome = Outcome(True, 'Got feed.')

class Combo:
    def __init__(self, feed, jar, sub):
        '''Constructs a container holding all combined feed and jar 
        entries. Copies feed then adds non-duplicates from jar'''
        if hasattr(sub, 'from_the_top'):
            self.lst = list(jar.lst)
            self.lst.extend(uid for uid in feed.lst if uid not in jar.lst)
        else:
            self.lst = list(feed.lst)
            self.lst.extend(uid for uid in jar.lst if uid not in feed.lst)
        self.dic = {uid: entryinfo.expand(feed.dic[uid], sub) 
            for uid in feed.lst if uid not in jar.lst}
        # remove from list entries with entry['valid'] = False?
        self.dic.update(jar.dic)

class Wanted():
    def __init__(self, sub, combo, del_lst):
        # listing filters
        match_filename = lambda x: bool(re.search(sub.filters['filename'], 
            combo.dic[x]['poca_filename']))
        match_title = lambda x: bool(re.search(sub.filters['title'], 
            combo.dic[x]['title']))
        match_hour = lambda x: str(combo.dic[x]['updated_parsed'].tm_hour) \
            == sub.filters['hour']
        match_wdays = lambda x: str(combo.dic[x]['updated_parsed'].tm_wday) \
            in list(sub.filters['weekdays'])
        cutoff_date = lambda x: (combo.dic[x]['published_parsed']) \
            > sub.filters['after_date']
        deletions = lambda x: x not in del_lst
        # applying filters
        self.lst = combo.lst
        # First we remove the ones that have been deleted. These are obviously
        # out regardless of other criteria.
        self.lst = list(filter(deletions, self.lst))
        # Note that after_date evaluates each entry on it's own merits. In
        # other words it is not positional (all entries after x in list...) 
        # Thus it should work with from_the_top. In effect though it should 
        # divide the list in two and only keep one part.
        if 'after_date' in sub.filters:
            self.lst = list(filter(cutoff_date, self.lst))
        # The following optional filters should remove various entries from
        # the list in no particular order.
        if 'filename' in sub.filters:
            self.lst = list(filter(match_filename, self.lst))
        if 'title' in sub.filters:
            self.lst = list(filter(match_title, self.lst))
        if 'hour' in sub.filters:
            self.lst = list(filter(match_hour, self.lst))
        if 'weekdays' in sub.filters:
            self.lst = list(filter(match_wdays, self.lst))
        # Lastly we limit the number of files. This has to come last as 
        # otherwise the final number might get reduced further. Also this is
        # now the ONLY positional filter so there's no chance of multiple 
        # positional filters interacting in weird ways.
        if sub.max_no:
            self.lst = self.lst[:int(sub.max_no)]
        # Currently wwe just copy the whole b***** dic. Later on we will 
        # reduce it by only taking on the ones with keys matching self.lst
        self.dic = combo.dic

