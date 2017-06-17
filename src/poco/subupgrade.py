# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Operations on feeds with updates"""


from poco import files, output, tag


class SubUpgrade():
    def __init__(self):
        '''Act on the plans laid out'''
        # loop through user deleted and indicate recognition
        for entry in self.udeleted:
            output.notice_udeleted(entry)

        # prepare list for summary
        self.removed, self.downed, self.failed = [], [], []

        # loop through unwanted (set) entries to remove
        for uid in self.unwanted:
            entry = self.jar.dic[uid]
            self.remove(uid, entry)
            if not self.outcome.success:
                output.suberror(self.ctitle, self.outcome)
                return

        # loop through wanted (list) entries to acquire
        # WHY OH WHY aren't we just looping through lacking? we still have 
        # access to wanted's dictionary?
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
                                              self.conf.xml.settings)

        # print summary of operations in file log
        output.summary(self.ctitle, self.udeleted, self.removed,
                       self.downed, self.failed)


    def acquire(self, uid, entry):
        '''Get new entries, tag them and add to history'''
        # see https://github.com/brokkr/poca/wiki/Architecture#wantedindex
        output.downloading(entry)
        wantedindex = self.wanted.lst.index(uid) - len(self.failed)
        outcome = files.download_file(entry['poca_url'],
                                      entry['poca_abspath'],
                                      self.conf.xml.settings)
        if outcome.success:
            outcome = tag.tag_audio_file(self.conf.xml.settings,
                                         self.sub, self.jar, entry)
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

