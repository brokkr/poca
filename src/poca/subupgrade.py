# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Operations on feeds with updates"""


from threading import Thread, current_thread
from poca import files, output, tag
from poca.outcome import StateInfo


class SubUpgradeThread(Thread):
    '''A thread class that creates handles a SubData instance'''
    def __init__(self, update_q, target, *args):
        self.update_q = update_q
        self.target = target
        self.args = args
        super(SubUpgradeThread, self).__init__()

    def run(self):
        sub_upgrade = self.target(*self.args)
        self.update_q.task_done()


class SubUpgrade():
    '''Use the SubData packet to implement file operations'''
    def __init__(self, state_q, subdata, dl_settings, id3_settings):

        # know thyself
        self.my_thread = current_thread()

        # loop through user deleted and indicate recognition
        udeleted = subdata.get_udeleted()
        for guid in udeleted:
            it = subdata.items[guid]
            output.processing_user_deleted(it)
        if udeleted:
            its = [subdata.items[guid] for guid in udeleted]
            state_q.put(StateInfo(subdata.title, 'udeleted', its))

        # loop through unwanted (set) entries to remove
        for guid in subdata.get_trash():
            it = subdata.items[guid]
            self.remove(it)
        removed = subdata.get_removed()
        if removed:
            its = [subdata.items[guid] for guid in removed]
            state_q.put(StateInfo(subdata.title, 'removed', its))

        # loop through lacking to retrieve
        for guid in subdata.get_lacking():
            it = subdata.items[guid]
            dl_outcome = self.acquire(dl_settings, it)
            if not dl_outcome.success:
                continue
            if not 'metadata' in subdata.sub:
                continue
            tag_outcome = tag.tag_audio_file(id3_settings, subdata.sub, it)
            if not tag_outcome.success:
                output.fail_tag(subdata.title, tag_outcome)
        retrieved = subdata.get_retrieved()
        if retrieved:
            its = [subdata.items[guid] for guid in retrieved]
            print(its)
            state_q.put(StateInfo(subdata.title, 'retrieved', its))

        # assuming we made it this far, we update etag, modified etc.
        state_q.put(StateInfo(subdata.title, 'feed', subdata.feedstatus))

        # save etag and subsettings after succesful update
        #if self.fail_flag is False:
        #    subdata.jar.sub = subdata.sub
        #    subdata.jar.etag = subdata.wanted.feed_etag
        #    subdata.jar.modified = subdata.wanted.feed_modified
        #_outcome = subdata.jar.save()
        #if _outcome.success is False:
        #    output.fail_database(_outcome)

        # download cover image (maybe throw in useragent?)
        #if self.downed and subdata.wanted.feed_image:
        #    _outcome = files.download_img_file(subdata.wanted.feed_image,
        #                                       subdata.sub_dir)
        #    if _outcome.success is False:
        #        output.fail_download(subdata.sub['title'], _outcome)

        # print summary of operations in file log
        output.file_summary(subdata)

    def acquire(self, dl_settings, it):
        '''Get new entries, tag them and add to history'''
        output.processing_download(it)
        #wantedindex = subdata.wanted.lst.index(uid) - len(self.failed)
        # see https://github.com/brokkr/poca/wiki/__Developer-notes__
        outcome = files.download_file(dl_settings, it)
        if outcome.success is False:
            filename, it.path = ('', '')
            output.fail_download(it, outcome)
            return outcome
        if outcome.success is None:
            return outcome
        else:
            filename, it.path = outcome.msg
            it.end_retrieved = True
            return outcome
        #subdata.jar.lst.insert(wantedindex, uid)
        #subdata.jar.dic[uid] = entry
        #_outcome = subdata.jar.save()
        #if _outcome.success is False:
        #    self.fail_flag = True
        #    output.fail_database(_outcome)

    def remove(self, it):
        '''Deletes the file and removes the entry from the jar'''
        self.outcome = files.delete_file(it)
        if self.outcome.success is False:
            output.fail_delete(it, self.outcome)
            return
        it.end_removed = True
        output.processing_removal(it)
        #subdata.jar.lst.remove(uid)
        #del(subdata.jar.dic[uid])
        #_outcome = subdata.jar.save()
        #if _outcome.success is False:
        #    self.fail_flag = True
        #    output.fail_database(_outcome)
