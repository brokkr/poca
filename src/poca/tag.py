# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Editing metadata on music files"""

import mutagen

from poca.valid_tags import validate_keys
from poca.outcome import Outcome


def tag_audio_file(settings, sub, jar, entry):
    '''Metadata tagging using mutagen'''
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[settings.id3removev1.text]
    id3v2 = int(settings.id3v2version)
    tracks = sub.find('./track_numbering')
    tracks = tracks.text if tracks else 'no'
    frames = sub.xpath('./metadata/*')
    tags = [override.tag for override in frames]
    if not frames and tracks == 'no':
        return Outcome(True, 'Tagging skipped')
    # get access to metadata
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
    # easify
    if isinstance(audio, mutagen.mp3.MP3):
        if id3v2 == 3:
            audio.tags.update_to_v23()
        elif id3v2 == 4:
            audio.tags.update_to_v24()
        if 'comment' in tags:
            audio.tags.delall('COMM')
        if 'toc' in tags:
            audio.tags.delall('CTOC')
            audio.tags.delall('CHAP')
        audio.save(v1=id3v1, v2_version=id3v2)
        audio = mutagen.File(entry['poca_abspath'], easy=True)
    if isinstance(audio, mutagen.mp4.MP4):
        audio = mutagen.File(entry['poca_abspath'], easy=True)
    # validate the fields and file type
    audio_type = type(audio)
    outcome, overrides, invalid_keys = validate_keys(audio_type, frames)
    if outcome.success is False:
        return outcome
    # run overrides
    for override in overrides:
        # this where we should distinguish between empty strings and not
        # if opverride[1] then write, else delete/skip
        # question is: can we remove frames using easyid3
        # seems answer is no
        # so do we go back to reloading as straight ID3?
        # could be useful for collecting all non-easy tasks incl. comment
        # easy takes care of registered easy keys, leaving the rest to ID3
        # we pop instead of loop: this way it's easy (NPI) to see what's left
        # easy function adds recognised tags with empty strings to special list
        # that gets added back unto overrides át finish
        # challenge: we would need a translation of easy keys back to ID3 keys.
        # sure it's in there somewhere, right?
        audio[override[0]] = override[1]
    if tracks == 'yes' or (tracks == 'if missing' and 'tracknumber' not in
                           audio):
        track_no = jar.track_no if hasattr(jar, 'track_no') else 0
        track_no += 1
        jar.track_no = track_no
        jar.save()
        if isinstance(audio, (mutagen.mp3.EasyMP3, mutagen.oggvorbis.OggVorbis,
                              mutagen.oggopus.OggOpus, mutagen.flac.FLAC)):
            audio['tracknumber'] = str(track_no)
        # else?
    # save and finish
    if isinstance(audio, mutagen.mp3.EasyMP3):
        audio.save(v1=id3v1, v2_version=id3v2)
    else:
        audio.save()
    if not invalid_keys:
        return Outcome(True, 'Metadata successfully updated')
    else:
        return Outcome(False, '%s is set to add invalid tags: %s' %
                       (sub.title.text, ', '.join(invalid_keys)))
