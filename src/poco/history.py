# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Keeping records of downloaded files"""

import os
import pickle

from poco import files
from poco.outcome import Outcome

def open_jar(db_filename):
    '''Tries opening existing jar'''
    try:
        with open(db_filename, mode='rb') as f:
            jar = pickle.load(f)
            outcome = Outcome(True, 'Pickle loaded')
    except (PermissionError, pickle.UnpicklingError, EOFError) as e:
        outcome = Outcome(False, str(e))
        jar = None
    return jar, outcome

def get_subjar(paths, sub):
    '''Returns existing jar if any, else creates a new one'''
    db_filename = os.path.join(paths.db_dir, sub.title.text)
    if os.path.isfile(db_filename):
        jar, outcome = open_jar(db_filename)
    else:
        jar = Subjar(paths, sub)
        outcome = jar.save()
    return jar, outcome

class Subjar:
    '''Creates standard subscription info container with save method'''
    def __init__(self, paths, sub):
        self.db_filename = os.path.join(paths.db_dir, sub.title.text)
        self.sub = sub
        self.etag = None
        self.lst = []
        self.dic = {}
        self.del_lst = []
        self.del_dic = {}

    def save(self):
        '''Saves jar instance to file using pickle'''
        outcome = files.check_path(os.path.dirname(self.db_filename))
        if outcome.success:
            #try:
            with open(self.db_filename, 'wb') as f:
                pickle.dump(self, f)
            outcome = Outcome(True, 'Pickle successful')
            # need more specific exceptions here
            #except:
            #    outcome = Outcome(False, 'Pickle failed')
        return outcome

class Jar(Subjar):
    '''Old name for Subjar. Needed for unpickling old instances'''
    pass

def get_statejar(paths):
    '''Returns existing jar if any, else creates a new one'''
    db_filename = os.path.join(paths.db_dir, '.poca')
    if os.path.isfile(db_filename):
        jar, outcome = open_jar(db_filename)
    else:
        jar = Statejar(db_filename)
        outcome = jar.save()
    return jar, outcome

class Statejar:
    '''Creates standard subscription info container with save method'''
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.buffer = []

    def save(self):
        '''Saves jar instance to file using pickle'''
        outcome = files.check_path(os.path.dirname(self.db_filename))
        if outcome.success:
            with open(self.db_filename, 'wb') as f:
                pickle.dump(self, f)
            outcome = Outcome(True, 'Pickle successful')
        return outcome
