# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Lists of valid tagging keys for reference"""

import mutagen


mp3_list = list(mutagen.easyid3.EasyID3.valid_keys.keys())
mp4_list = ['title', 'album', 'artist', 'albumartist', 'date', 'comment',
            'description', 'grouping', 'genre', 'copyright', 'albumsort',
            'albumartistsort', 'artistsort', 'titlesort', 'composersort']
def mp3_keys(key): yield key if key in mp3_list else None
def mp4_keys(key): yield key if key in mp4_list else None
def vorbis_keys(key): yield key
type_dic = {mutagen.mp3.EasyMP3: mp3_keys,
            mutagen.easymp4.EasyMP4: mp4_keys,
            mutagen.oggvorbis.OggVorbis: vorbis_keys,
            mutagen.oggopus.OggOpus: vorbis_keys,
            mutagen.flac.FLAC: vorbis_keys}

def validate_keys(audio_type, frames):
    '''Returns a tuple with valid overrides and a list of invalid keys'''
    valid_keys = type_dic.get(audio_type, None)
    if valid_keys is None:
        return (Outcome(False, 'Unsupported file type for tagging'), [], [])
    overrides = [(override.tag, override.text) for override in frames
                 if override.tag in valid_keys(override.tag)]
    invalid_keys = [override.tag for override in frames if override.tag
                    not in valid_keys)
    return (Outcome(True, 'Valid audio type'), overrides, invalid_keys)
