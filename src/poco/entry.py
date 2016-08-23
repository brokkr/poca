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


def attach_size(self, mega):
    '''Expands entry with url and size'''
    self['valid'] = True
    try:
        self['poca_url'] = self.enclosures[0]['href']
    except (KeyError, IndexError, AttributeError):
        self['valid'] = False
        return
    try:
        self['poca_size'] = int(self.enclosures[0]['length'])
        if self['poca_size'] == 0:
            raise ValueError
    except (KeyError, ValueError):
        try:
            f = urllib.request.urlopen(self['poca_url'])
            self['poca_size'] = int(f.info()['Content-Length'])
            f.close()
        except (urllib.error.HTTPError, urllib.error.URLError):
            self['valid'] = False
    if self['valid']:
        self['poca_mb'] = round(self.poca_size / mega, 2)

def attach_path(self, sub):
    '''Expands entry with file name and path'''
    parsed_url = urllib.parse.urlparse(self['poca_url'])
    self['poca_filename'] = path.basename(parsed_url.path)
    self['poca_basename'] = self['poca_filename'].split('.')[0]
    self['poca_ext'] = path.splitext(self['poca_filename'])[1].lower()
    self['poca_abspath'] = path.join(sub.sub_dir, self['poca_filename'])

