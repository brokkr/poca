#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.


import pickle
from os import path

def get_jar(paths, sub):
    filename = path.join(paths.db_dir, sub.title)
    if path.isfile(filename):
        with open(filename, 'r') as f:
            jar = pickle.load(f)
    else:
        jar = NewJar(filename)
    return jar

class NewJar:
    def __init__(self, filename):
        self.filename = filename
        self.lst = []
        self.dic = {}
        self.save()

    def save(self):
        with open(self.filename, 'w') as f:
            pickle.dump(self, f)

