# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Editing metadata on music files"""

import mutagen

from poca.outcome import Outcome


def tag_audio_file(settings, sub, jar, entry):
    '''Metdata tagging using mutagen'''
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[settings.id3removev1.text]
    id3v2 = int(settings.id3v2version)
    tracks = sub.find('./track_numbering')
    tracks = tracks.text if tracks else 'no'
    frames = sub.xpath('./metadata/*')
    if not frames and tracks == 'no':
        return Outcome(True, 'Tagging skipped')
    try:
        audio = mutagen.File(entry['poca_abspath'])
    except mutagen.MutagenError:
        return Outcome(False, '%s not found or invalid file type for tagging'
                       % entry['poca_abspath'])
    except mutagen.mp3.HeaderNotFoundError:
        return Outcome(False, '%s bad mp3'
                       % entry['poca_abspath'])
    if audio is None:
        return Outcome(False, '%s is invalid file type for tagging' %
                       entry['poca_abspath'])
    if audio.tags is None:
        audio.add_tags()
    if isinstance(audio, mutagen.mp3.MP3):
        if id3v2 == 3:
            audio.tags.update_to_v23()
        elif id3v2 == 4:
            audio.tags.update_to_v24()
        audio.save(v1=id3v1, v2_version=id3v2)
        audio = mutagen.File(entry['poca_abspath'], easy=True)
    if isinstance(audio, mutagen.mp3.EasyMP3):
        overrides = [(override.tag, override.text) for override in frames
                     if override.tag in audio.tags.valid_keys.keys()]
    else:
        overrides = [(override.tag, override.text) for override in frames]
    for override in overrides:
        audio[override[0]] = override[1]
    if tracks == 'yes' or (tracks == 'if missing' and 'tracknumber' not in
                           audio):
        track_no = jar.track_no if hasattr(jar, 'track_no') else 0
        track_no += 1
        jar.track_no = track_no
        jar.save()
        audio['tracknumber'] = str(track_no)
    if isinstance(audio, mutagen.mp3.EasyMP3):
        audio.save(v1=id3v1, v2_version=id3v2)
    else:
        audio.save()
    return Outcome(True, 'Metadata successfully updated')
