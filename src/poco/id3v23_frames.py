#!/usr/bin/env python2                                                                                                                           
#                                                                                    
# Copyright 2010, 2011, 2015 Mads Michelsen (reannual@gmail.com)                     
#                                                                                    
# This file is part of Poca.                                                         
# Poca is free software: you can redistribute it and/or modify it under the terms \  
# of the GNU General Public License as published by the Free Software Foundation, \  
# either version 3 of the License, or (at your option) any later version. 

from mutagen import id3

# translation taken from http://puddletag.sourceforge.net/source/id3.html
# originally licensed under Apache License version 2.0

frame_dic = { \
    "album": id3.TALB,
    "albumartist": id3.TPE2,
    "albumsortorder": id3.TSOA,
    "arranger": id3.TPE4,
    "artist": id3.TPE1,
    "audiodelay": id3.TDLY,
    "audiolength": id3.TLEN,
    "audiosize": id3.TSIZ,
    "author": id3.TOLY,
    "bpm": id3.TBPM,
    "composer": id3.TCOM,
    "conductor": id3.TPE3,
    "copyright": id3.TCOP,
    "date": id3.TDAT,
    "discnumber": id3.TPOS,
    "encodedby": id3.TENC,
    "encodingsettings": id3.TSSE,
    "filename": id3.TOFN,
    "fileowner": id3.TOWN,
    "filetype": id3.TFLT,
    "genre": id3.TCON,
    "grouping": id2.TIT1,
    "initialkey": id3.TKEY,
    "isrc": id3.TSRC,
    "itunesalbumsortorder": id3.TSO2,
    "itunescompilationflag": id3.TCMP,
    "itunescomposersortorder": id3.TSOC,
    "language": id3.TLAN,
    "lyricist": id3.TEXT,
    "mediatype": id3.TMED,
    "mood": id3.TMOO,
    "organization": id3.TPUB,
    "originalalbum": id3.TOAL,
    "originalartist": id3.TOPE,
    "originalyear": id3.TORY,
    "performersortorder": id3.TSOP,
    "producednotice": id3.TPRO,
    "radioowner": id3.TRSO,
    "radiostationname": id3.TRSN,
    "recordingdates": id3.TRDA,
    "setsubtitle": id3.TSST,
    "time": id3.TIME,
    "title": id3.TIT2,
    "titlesortorder": id3.TSOT,
    "track": id3.TRCK,
    "version": id3.TIT3,
    "year": id3.TYER 
}
