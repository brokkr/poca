# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Editing metadata on music files"""

import mutagen

#from poco.id3v24_frames import FRAME_DIC
from poco.outcome import Outcome


def tag_audio_file(settings, sub, entry):
    '''Reintroducing id3 tagging using mutagen'''
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[settings.id3removev1.text]
    id3encoding_dic = {'latin1': 0, 'utf8': 3}
    id3encoding = id3encoding_dic[settings.id3encoding.text]
    audio = mutagen.File(entry['poca_abspath'], easy=True)
    if audio is None:
        return Outcome(False, 'Invalid file type')
    if audio.tags is None:
        audio.add_tags()
    if isinstance(audio, mutagen.mp3.EasyMP3):
        overrides = [(override.tag, override.text) for override in
                     sub.metadata.iterchildren() if override.tag in
                     audio.tags.valid_keys.keys()]
    else:
        overrides = [(override.tag, override.text) for override in
                     sub.metadata.iterchildren()]
    if isinstance(audio, mutagen.oggvorbis.OggVorbis):
        pass
    if isinstance(audio, mutagen.oggopus.OggOpus):
        pass
    if isinstance(audio, mutagen.flac.FLAC):
        pass
    for override in overrides:
        audio[override[0]] = override[1]
    if isinstance(audio, mutagen.mp3.EasyMP3):
        audio.save(v1=id3v1, v2_version=4)
    else:
        audio.save()
    return Outcome(True, 'Metadata successfully updated')


    #except UnicodeEncodeError:
    #    return Outcome(False, 'Unicode overrides in non-Unicode encoding')
    #if failure_lst:
    #    return Outcome(False, 'Bad overrides: ' + str(failure_lst))
    #else:
    #    return Outcome(True, 'Metadata successfully updated')
