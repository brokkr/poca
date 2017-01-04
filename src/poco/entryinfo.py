# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

from os import path
import urllib.request, urllib.error, urllib.parse


def expand(entry, sub):
    '''Expands entry with url, paths and size'''
    try:
        entry['poca_url'] = entry.enclosures[0]['href']
        entry['valid'] = True
    except (KeyError, IndexError, AttributeError):
        entry['valid'] = False
        #for key in entry:
        #    print(key, ' : ', entry[key])
        return entry
    try:
        entry['poca_size'] = int(entry.enclosures[0]['length'])
        if entry['poca_size'] == 0:
            raise ValueError
        entry['poca_mb'] = round(entry.poca_size / 1048576.0, 2)
    except (KeyError, ValueError, TypeError):
        entry['poca_size'] = None
        entry['poca_mb'] = None
    parsed_url = urllib.parse.urlparse(entry['poca_url'])
    entry['poca_filename'] = path.basename(parsed_url.path)
    entry['poca_basename'] = entry['poca_filename'].split('.')[0]
    entry['poca_ext'] = path.splitext(entry['poca_filename'])[1].lower()
    entry['poca_abspath'] = path.join(sub.sub_dir, entry['poca_filename'])
    entry['valid'] = True
    return entry

