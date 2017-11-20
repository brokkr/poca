# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Operations on feeds with updates"""


from threading import Thread, current_thread
from poca import files, output, tag


class SubUpgradeThread(Thread):
    '''A thread class that creates handles a SubData instance'''
    def __init__(self, subdata, queue, target):
        self.subdata = subdata
        self.queue = queue
        self.target = target
        super(SubUpgradeThread, self).__init__()

    def run(self):
        sub_upgrade = self.target(self.subdata)
        self.queue.task_done()


class SubUpgrade():
    '''Use the SubData packet to implement file operations'''
    def __init__(self, subdata):

        # know thyself
        self.my_thread = current_thread()

        # prepare list for summary
        self.fail_flag = False
        self.removed, self.downed, self.failed = [], [], []

        # loop through user deleted and indicate recognition
        for entry in subdata.udeleted:
            output.processing_user_deleted(entry)

        # loop through unwanted (set) entries to remove
        for uid in subdata.unwanted:
            entry = subdata.jar.dic[uid]
            self.remove(uid, entry, subdata)

        for uid in subdata.lacking:
            entry = subdata.wanted.dic[uid]
            self.acquire(uid, entry, subdata)
            if self.outcome.success is None:
                return

        # save etag and subsettings after succesful update
        if self.fail_flag is False:
            subdata.jar.sub = subdata.sub
            subdata.jar.etag = subdata.wanted.feed_etag
            subdata.jar.modified = subdata.wanted.feed_modified
        _outcome = subdata.jar.save()
        if _outcome.success is False:
            output.fail_database(_outcome)

        # download cover image
        if self.downed and subdata.wanted.feed_image:
            _outcome = files.download_img_file(subdata.wanted.feed_image,
                                               subdata.sub_dir,
                                               subdata.conf.xml.settings)
            if _outcome.success is False:
                output.fail_download(subdata.sub.title.text, _outcome)

        # print summary of operations in file log
        output.file_summary(subdata, self.removed, self.downed, self.failed)

    def acquire(self, uid, entry, subdata):
        '''Get new entries, tag them and add to history'''
        output.processing_download(entry)
        wantedindex = subdata.wanted.lst.index(uid) - len(self.failed)
        # see https://github.com/brokkr/poca/wiki/__Developer-notes__
        self.outcome = files.download_file(entry['poca_url'],
                                           entry['poca_abspath'],
                                           subdata.conf.xml.settings)
        if self.outcome.success is False:
            self.fail_flag = True
            output.fail_download(subdata.sub.title.text, self.outcome)
            self.failed.append(entry)
            return
        if self.outcome.success is None:
            return
        subdata.jar.lst.insert(wantedindex, uid)
        subdata.jar.dic[uid] = entry
        _outcome = subdata.jar.save()
        if _outcome.success is False:
            self.fail_flag = True
            output.fail_database(_outcome)
        self.downed.append(entry)
        _outcome = tag.tag_audio_file(subdata.conf.xml.settings,
                                      subdata.sub, subdata.jar, entry)
        if not _outcome.success:
            output.fail_tag(subdata.sub.title.text, _outcome)

    def remove(self, uid, entry, subdata):
        '''Deletes the file and removes the entry from the jar'''
        self.outcome = files.delete_file(entry['poca_abspath'])
        if self.outcome.success is False:
            self.fail_flag = True
            output.fail_delete(subdata.sub.title.text, self.outcome)
            return
        output.processing_removal(entry)
        self.removed.append(entry)
        subdata.jar.lst.remove(uid)
        del(subdata.jar.dic[uid])
        _outcome = subdata.jar.save()
        if _outcome.success is False:
            self.fail_flag = True
            output.fail_database(_outcome)
