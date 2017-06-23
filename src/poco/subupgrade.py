# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Operations on feeds with updates"""


from threading import Thread
from poco import files, output, tag


class SubUpgradeThread(Thread):
    '''A thread class that creates handles a SubData instance'''
    def __init__(self, queue, target):
        self.queue = queue
        self.target = target
        super(SubUpgradeThread, self).__init__()

    def run(self):
        subdata = self.queue.get()
        if subdata.outcome.success:
            output.subplans(subdata)
            sub_upgrade = self.target(subdata)
        else:
            output.suberror(subdata)
        self.queue.task_done()

class SubUpgrade():
    '''Use the SubData packet to implement file operations'''
    def __init__(self, subdata):
        # prepare list for summary
        self.removed, self.downed, self.failed = [], [], []

        # loop through user deleted and indicate recognition
        for entry in subdata.udeleted:
            output.notice_udeleted(entry)

        # loop through unwanted (set) entries to remove
        for uid in subdata.unwanted:
            entry = subdata.jar.dic[uid]
            self.remove(uid, entry, subdata)
            if not self.outcome.success:
                output.suberror(subdata)
                return

        # loop through wanted (list) entries to acquire
        # WHY OH WHY aren't we just looping through lacking? we still have
        # access to wanted's dictionary?
        for uid in subdata.wanted.lst:
            if uid not in subdata.lacking:
                continue
            entry = subdata.wanted.dic[uid]
            self.acquire(uid, entry, subdata)

        # save etag and subsettings after succesful update
        if not self.failed:
            subdata.jar.sub = subdata.sub
            subdata.jar.etag = subdata.wanted.feed_etag
        subdata.jar.save()

        # download cover image
        if self.downed and subdata.wanted.feed_image:
            outcome = files.download_img_file(subdata.wanted.feed_image,
                                              subdata.sub_dir,
                                              subdata.conf.xml.settings)

        # print summary of operations in file log
        output.summary(subdata, self.removed, self.downed, self.failed)
        # we need to gather up failed errors for a presentation after all
        # threads have ended. There are two ways to do this:
        # 1) Throw in another queue to stuff them down
        # 2) Throw in another filelogger to write them to, then print it 
        # out after all threads have ended.
        # Advantage of 1 is that it can be used to all kinds of communication
        # Advantage of 2 is that it seems more 'logical' to use loggers 
        # seeing as it is a logging issue
        # Actually we don't need a file logger, we need a buffering logger


    def acquire(self, uid, entry, subdata):
        '''Get new entries, tag them and add to history'''
        # see https://github.com/brokkr/poca/wiki/Architecture#wantedindex
        output.downloading(entry)
        wantedindex = subdata.wanted.lst.index(uid) - len(self.failed)
        outcome = files.download_file(entry['poca_url'],
                                      entry['poca_abspath'],
                                      subdata.conf.xml.settings)
        if outcome.success:
            outcome = tag.tag_audio_file(subdata.conf.xml.settings,
                                         subdata.sub, subdata.jar, entry)
            if not outcome.success:
                output.tag_fail(outcome)
                # add to failed? no, it would mess with wanted_index
            self.add_to_jar(uid, entry, wantedindex, subdata)
            self.downed.append(entry)
        else:
            output.dl_fail(outcome)
            self.failed.append(entry)

    def add_to_jar(self, uid, entry, wantedindex, subdata):
        '''Add new entry to jar'''
        subdata.jar.lst.insert(wantedindex, uid)
        subdata.jar.dic[uid] = entry
        self.outcome = subdata.jar.save()
        # currently no jar-save checks

    def remove(self, uid, entry, subdata):
        '''Deletes the file and removes the entry from the jar'''
        output.removing(entry)
        self.outcome = files.delete_file(entry['poca_abspath'])
        if not self.outcome.success:
            return
        subdata.jar.lst.remove(uid)
        del(subdata.jar.dic[uid])
        self.outcome = subdata.jar.save()
        # currently no jar-save checks
        self.removed.append(entry)
