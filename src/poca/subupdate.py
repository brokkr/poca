# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
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
from poca import files, item
from poca.outcome import Outcome, FeedStatus


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
    def __init__(self, sub, defaults, state, base_dir):
        self.sub = sub
        self.title = sub['title']
        self.defaults = defaults
        self.state = state

        # merge sub settings and defaults
        #defaults = deepcopy(self.conf.xml.defaults)
        #rename = deepcopy(self.sub.rename) if hasattr(self.sub, 'rename') \
        #    else None
        #errors = merge(self.sub, defaults, self.conf.xml.defaults, errors=[])
        #self.outcome = errors[0] if errors else Outcome(True, '')
        #defaults.tag = "subscription"
        #self.sub = defaults
        #if rename is not None:
        #    self.sub.rename = rename
        #if not self.outcome.success:
        #    return

        # parsing response and saving feed status
        new_url, exception = (None, None)
        doc = feedparser.parse(sub['url'], etag=state['etag'], \
                               modified=state['modified'])
        if doc.status == 301:
            self.outcome = Outcome(True, 'Feed has moved')
            new_url = getattr(doc, 'href', sub['url'])
        elif doc.status == 304:
            self.outcome = Outcome(True, 'Not modified')
            return
        # 410 -> set to inactive
        elif doc.status >= 400:
            exception = doc.feed.bozo_exception
            self.outcome = Outcome(False, exception)
            return
        else:
            self.outcome = Outcome(True, 'Success')
        try:
            image_href = doc.feed.image['href']
        except (AttributeError, KeyError):
            image_href = None
        etag = doc.etag if hasattr(doc, 'etag') else None
        modified = doc.modified if hasattr(doc, 'modified') else None
        self.feedstatus = FeedStatus(doc.status, new_url, exception,
                                     image_href, etag, modified)

        # before we moved to overwriting feed with state info...
        #for guid in set(state['current']).intersection(items.keys()):
        #    items[guid].set_current(state['current'].pop(guid))
        #remainder = {guid: item.Item(state['current'][guid]) for guid in
        #             state['current']})

        # "combo"
        self.items = {entry.guid: item.Item(entry) for entry in doc.entries}
        current = {guid: item.CurrentItem(guid, state['current'][guid]) for \
                   guid in state['current']}
        blocked = {guid: item.BlockedItem(guid) for guid in state['blocked']}
        print(type(self.items), type(current), type(blocked))
        # add: loop through current, converting to blocked as needed
        self.items.update(current)
        self.items.update(blocked)

        # validation
        for guid in [guid for guid in self.items if not
                     self.items[guid].type_blocked]:
            it = self.items[guid]
            it.validate()
            it.filter_vars()

        # wanted
        if 'filters' in self.sub:
            self.apply_filters()
        # inclusion
        if 'max_number' in self.sub:
            self.limit()
        for guid in [guid for guid in self.items if
                     self.items[guid].stage_included]:
            self.items[guid].extra_vars(sub, doc.feed)
            self.items[guid].generate_names(base_dir, sub)

        #filenames = [self.dic[uid]['poca_filename'] for uid in self.lst]
        #for uid in self.lst:
        #    count = filenames.count(self.dic[uid]['poca_filename'])
        #    if count > 1:
        #        self.dic[uid]['unique_filename'] = False
        #    else:
        #        self.dic[uid]['unique_filename'] = True

        #from_the_top = self.sub.find('from_the_top') or 'no'
        #if from_the_top == 'no':
        #    self.wanted.lst.reverse()

        # subupgrade will delete unwanted and download lacking
        #self.unwanted = [x for x in self.jar.lst if x not in self.wanted.lst]
        #self.lacking = [x for x in self.wanted.lst if x not in self.jar.lst]

    def apply_filters(self):
        '''Apply all filters set to be used on the subscription'''
        func_dic = {'after_date': self.match_date,
                    'filename': self.match_filename,
                    'title': self.match_title,
                    'hour': self.match_hour,
                    'weekdays': self.match_weekdays}
        filters = self.sub['filters'].keys()
        valid_filters = filters & set(func_dic.keys())
        for guid in [guid for guid in self.items if
                     self.items[guid].stage_valid]:
            it = self.items[guid]
            tests = list()
            for key in valid_filters:
                try:
                    tests.append(func_dic[key](it, self.sub['filters'][key]))
                    self.outcome = Outcome(True, 'Filters applied successfully')
                except KeyError as e:
                    self.outcome = Outcome(False, 'Entry is missing info: %s' % e)
                except (ValueError, TypeError, SyntaxError) as e:
                    self.outcome = Outcome(False, 'Bad filter setting: %s' % e)
            if all(tests):
                it.stage_wanted = True
    #def check_jar(self):
    #    '''Check for user deleted files so we can filter them out'''
    #    for uid in self.jar.lst:
    #        entry = self.jar.dic[uid]
    #        outcome = files.verify_file(entry)
    #        if not outcome.success:
    #            self.udeleted.append(entry)
    #            self.jar.del_lst.append(uid)
    #            self.jar.del_dic[uid] = self.jar.dic.pop(uid)
    #    self.jar.lst = [x for x in self.jar.lst if x not in self.jar.del_lst]
    #    self.outcome = self.jar.save()

    def match_filename(self, it, filter_text):
        '''The episode filename must match a regex/string'''
        return bool(re.search(filter_text, it.variables['filename']))

    def match_title(self, it, filter_text):
        '''The episode title must match a regex/string'''
        return bool(re.search(filter_text, it.variables['title_episode']))

    def match_weekdays(self, it, filter_text):
        '''Only return episodes published on specific week days'''
        # careful: string or integer? (or make poca.yaml setting a list)
        return it.variables['weekday'] in list(filter_text)

    def match_date(self, it, filter_text):
        '''Only return episodes published after a specific date'''
        return it.variables['date'] > time.strptime(filter_text, '%Y-%m-%d')

    def match_hour(self, it, filter_text):
        '''Only return episodes published at a specific hour of the day'''
        return it.variables['hour'] == int(filter_text)

    def limit(self):
        '''Limit the number of episodes to that set in max_number'''
        try:
            wanted = [guid for guid in self.items if \
                      self.items[guid].stage_wanted]
            for guid in wanted[:int(self.sub['max_number'])]:
                self.items[guid].stage_included = True
            # don't overwrite filter failure
            if self.outcome.success:
                self.outcome = Outcome(True, 'Number limited successfully')
        except ValueError:
            self.outcome = Outcome(False, 'Bad max_number setting')

    # GET SLICES OF ITEMS

    def get_udeleted(self):
        return [guid for guid in self.items if self.items[guid].blocked and
                guid not in self.state['blocked'])

    def get_trash(self):
        return [guid for guid in self.items if self.items[guid].current and
                not self.items[guid].included)

    def get_lacking(self):
        return [guid for guid in self.items if self.items[guid].included and
                not self.items[guid].current)

