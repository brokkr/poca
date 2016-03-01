# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import os
import pickle

from poco import files
from poco.output import Outcome


def get_jar(paths, sub):
    db_filename = os.path.join(paths.db_dir, sub.title)
    if os.path.isfile(db_filename):
        with open(db_filename, 'r') as f:
            jar = pickle.load(f)
    else:
        jar = Jar(paths, sub)
        outcome = jar.save()
    return jar

class Jar:
    def __init__(self, paths, sub):
        self.db_filename = os.path.join(paths.db_dir, sub.title)
        self.lst = []
        self.dic = {}

    def save(self):
        outcome = files.check_path(os.path.dirname(self.db_filename))
        if outcome.success:
            try:
                with open(self.db_filename, 'w') as f:
                    pickle.dump(self, f)
                outcome = Outcome(True, 'Pickle successful')
            except:
                outcome = Outcome(False, 'Pickle failed')
        return outcome


