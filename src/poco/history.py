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

def get_jar(db_filename):
    if path.isfile(db_filename):
        with open(db_filename, 'r') as f:
            jar = pickle.load(f)
    else:
        jar = Jar(db_filename)
        jar.save()
    return jar

class Jar:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.lst = []
        self.dic = {}

    def save(self):
        with open(self.db_filename, 'w') as f:
            pickle.dump(self, f)

