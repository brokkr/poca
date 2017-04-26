# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Editing metadata on music files"""

import mutagen

from poco.id3v24_frames import FRAME_DIC
from poco.outcome import Outcome


def tag_audio_file(prefs, sub, entry):
    '''Reintroducing id3 tagging using mutagen'''
    # get general metadata settings
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[prefs.id3removev1.text]
    id3encoding_dic = {'latin1': 0, 'utf8': 3}
    id3encoding = id3encoding_dic[prefs.id3encoding]
    # check for proper header and metadata to apply
    if entry['poca_ext'] != '.mp3':
        return Outcome(True, 'Not an mp3')
    if not hasattr(sub, 'metadata'):
        return Outcome(True, 'No metadata overrides to apply')
    try:
        id3tag = mutagen.id3.ID3(entry['poca_abspath'])
    except mutagen.id3._util.ID3NoHeaderError:
        easytag = mutagen.File(entry['poca_abspath'], easy=True)
        easytag.add_tags()
        easytag['title'] = entry['poca_basename']
        easytag.save()
        id3tag = mutagen.id3.ID3(entry['poca_abspath'])
    id3tag.update_to_v24()
    # apply overrides to header and save file with chosen encoding
    for override in sub.metadata.iterchildren():
        failure_lst = []
        try:
            frame = FRAME_DIC[override.tag]
        except KeyError:
            failure_lst.append(override.tag)
            continue
        id3tag.add(frame(encoding=id3encoding, text=override.text))
    try:
        id3tag.save(v1=id3v1, v2_version=4)
    except UnicodeEncodeError:
        return Outcome(False, 'Unicode overrides in non-Unicode encoding')
    if failure_lst:
        return Outcome(False, 'Bad overrides: ' + str(failure_lst))
    else:
        return Outcome(True, 'Metadata successfully updated')
