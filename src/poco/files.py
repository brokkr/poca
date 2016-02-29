#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# except functions progress_download and silent_download copyright PabloG 
# (http://stackoverflow.com/users/394/pablog) and Mads Michelsen 2015
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import os
import shutil
import logging
import urllib2

import urllib

import mutagen

from poco.id3v23_frames import frame_dic
from poco import output


def check_path(check_dir):
    '''Create a directory'''
    if os.path.isdir(check_dir):
        return output.Outcome(True, 'Directory exists already')
    try:
        os.makedirs(check_dir)
        return output.Outcome(True, 'Directory was successfully created')
    except OSError, e:
        return output.Outcome(False, e)

def delete_file(filepath):
    '''Deletes a file'''
    try:
        os.remove(filepath)
        return output.Outcome(True, 'File was successfully deleted')
    except OSError:
        return output.Outcome(False, e)

def download_audio_file(args, entry):
    '''Downloads one file'''
    check_path(os.path.dirname(entry['poca_abspath']))
    try:
        u = urllib2.urlopen(entry['poca_url'])
        f = open(entry['poca_abspath'], 'w')
        meta = u.info()
        mega = 1048576.0
        file_size = int(meta.getheaders("Content-Length")[0]) / mega
        fsize_dl = 0
        block_sz = 65536
        # download chunks of block_size until there is no more to read
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            fsize_dl += len(buffer) / mega
            f.write(buffer)
            if not args.quiet:
                heading = "Downloading new file:    " + entry['poca_filename']
                status = (heading[0:59] + ' ').ljust(62,'.') + ("%7.2f Mb "
                    "[%3.0f%%]") % (fsize_dl, fsize_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                print status,
        f.close()
        if not args.quiet:
            print
        return output.Outcome(True, 'File was successfully downloaded')
    except urllib2.HTTPError, e:
        return output.Outcome(False, "HTTPError: " + e)
    except IOError, e:
        return output.Outcome(False, "IOError: " + e)

def tag_audio_file(sets_dic, entry_dic, sub_dic):
    '''Reintroducing id3 tagging using mutagen'''
    # get general metadata settings
    id3version_dic = {'2.3': 3, '2.4': 4}
    id3version = id3version_dic[sets_dic['metadata']['id3version']]
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[sets_dic['metadata']['removeid3v1']] 
    id3encoding = 0
    if sets_dic['metadata']['unicode'] == 'yes':
        id3encoding_dic = {3: 1, 4: 3}
        id3encoding = id3encoding_dic[id3version]
    # overwrite metadata in the present file 
    localfile = os.path.join(sub_dic['sub_dir'], entry_dic['filename'])
    file_extension = os.path.splitext(localfile)[1].lower()
    if file_extension != '.mp3':
        return
    if not sub_dic.has_key('metadata'):
        return
    try:
        id3tag = mutagen.id3.ID3(localfile)
    except mutagen.id3.ID3NoHeaderError:
        easytag = mutagen.File(localfile, easy=True)
        easytag.add_tags()
        easytag['title'] = os.path.basename(localfile).split('.')[0]
        easytag.save()
        id3tag = mutagen.id3.ID3(localfile)
    if id3version == 3:
        id3tag.update_to_v23()
    for override in sub_dic['metadata']:
        frame = frame_dic[override]
        ftext = sub_dic['metadata'][override]
        id3tag.add(frame(encoding=id3encoding, text=ftext))
        try:
            id3tag.save(v1=id3v1, v2_version=id3version)
        except UnicodeEncodeError:
            error = 'The metadata overrides contain Unicode characters\n\
but you have chosen a non-Unicode encoding.'
            suggest = ['Please change either your Unicode preference or \
your overrides']
            errors.errors(error, suggest)
            
def restart(paths_dic, subs_list):
    '''Deletes log file and all created directories'''
    try:
        sub_dir_list = [sub_dic['sub_dir'] for sub_dic in subs_list]
        print 'The following directories will be deleted:'
        for sub_dir in sub_dir_list:
            if os.path.isdir(sub_dir):
                print sub_dir
            else:
                sub_dir_list.remove(sub_dir)
        response = raw_input('Proceed? (y/n) ')
        if response.lower() != 'y':
            print 'Abandoning restart', '\n'
            return False
        print 'Deleting old files...', '\n'
        for sub_dir in sub_dir_list:
            shutil.rmtree(sub_dir)
        os.remove(paths_dic['history_log'])
        return True
    except OSError:
        return False

