# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Editing metadata on music files"""

import mutagen

from mutagen import id3, easyid3, easymp4
from poca.outcome import Outcome


encodings = {3: id3.Encoding.UTF16, 4: id3.Encoding.UTF8}
id3v1_dic = {'yes': 0, 'no': 2}

def tag_audio_file(settings, sub, jar, entry):
    '''Metadata tagging using mutagen'''
    # id3 settings
    id3v1 = id3v1_dic[settings.id3removev1.text]
    id3v2 = int(settings.id3v2version)
    id3encoding = encodings[id3v2]
    # overrides
    frames = sub.xpath('./metadata/*')
    overrides = [(override.tag, override.text) for override in frames]
    key_errors = {}
    # track numbering
    tracks = sub.find('./track_numbering')
    tracks = tracks.text if tracks else 'no'
    if not overrides and tracks == 'no':
        return Outcome(True, 'Tagging skipped')
    # get 'easy' access to metadata
    try:
        audio = mutagen.File(entry['poca_abspath'], easy=True)
    except mutagen.MutagenError:
        return Outcome(False, '%s not found or invalid file type for tagging'
                       % entry['poca_abspath'])
    except mutagen.mp3.HeaderNotFoundError:
        return Outcome(False, '%s is a bad mp3' % entry['poca_abspath'])
    if audio is None:
        return Outcome(False, '%s is invalid file type for tagging' %
                       entry['poca_abspath'])
    # add_tags is undocumented for easy but seems to work
    if audio.tags is None:
        audio.add_tags()
    # tracks
    if tracks == 'yes' or (tracks == 'if missing' and 'tracknumber' not in
                           audio):
        track_no = jar.track_no if hasattr(jar, 'track_no') else 0
        track_no += 1
        overrides.append(('tracknumber', str(track_no)))
        jar.track_no = track_no
        jar.save()
    # run overrides and save
    while overrides:
        tag, text = overrides.pop()
        if not text and tag in audio:
            _text = audio.pop(tag)
            continue
        try:
            audio[tag] = text
        except (easyid3.EasyID3KeyError, easymp4.EasyMP4KeyError, \
                ValueError) as e:
            key_errors[tag] = text
    audio.save()
    # ONLY for ID3
    if isinstance(audio, mutagen.mp3.EasyMP3):
        audio = mutagen.File(entry['poca_abspath'], easy=False)
        if 'comment' in key_errors:
            audio.tags.delall('COMM')
            comm_txt = key_errors.pop('comment')
            if comm_txt:
                comm = id3.COMM(encoding=id3encoding, lang='eng', \
                                desc='desc', text=comm_txt)
                audio.tags.add(comm)
        if 'chapters' in key_errors:
            _toc = key_errors.pop('chapters')
            audio.tags.delall('CTOC')
            audio.tags.delall('CHAP')
        if id3v2 == 3:
            audio.tags.update_to_v23()
        elif id3v2 == 4:
            audio.tags.update_to_v24()
        audio.save(v1=id3v1, v2_version=id3v2)
    # invalid keys
    invalid_keys = list(key_errors.keys())
    if not invalid_keys:
        return Outcome(True, 'Metadata successfully updated')
    else:
        return Outcome(False, '%s is set to add invalid tags: %s' %
                       (sub.title.text, ', '.join(invalid_keys)))
