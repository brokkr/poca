# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.


import yaml

from os import path
from pathlib import Path


class Update:
    def __init__(self, file_path, updates):
        with file_path.open(mode='r+') as f:
            self.state = yaml.safe_load(f)
            for update in updates:
                if update.job == 'feed':
                    self.feed(update)
                if update.job == 'removed':
                    self.remove(update)
                if update.job == 'retrieve':
                    self.add(update)
                if update.job == 'udeleted':
                    self.block(update)
            state_yaml = yaml.dump(self.state, allow_unicode=True)
            f.write(state_yaml)

    def feed(self, update):
        pass

    def remove(self, update):
        pass

    def add(self, update):
        pass

    def block(self, update):
        pass
