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
    def __init__(self, file_path, state_infos):
        with file_path.open(mode='r+') as f:
            self.state = yaml.safe_load(f)
            if self.state is None:
                self.state = dict()
            for state_info in state_infos:
                if not state_info.title in self.state:
                    self.state[state_info.title] = {'current': {}, 'blocked': []}
                sub = self.state[state_info.title]
                if state_info.job == 'feed':
                    self.feed(sub, state_info)
                if state_info.job == 'removed':
                    self.remove(sub, state_info)
                if state_info.job == 'retrieved':
                    self.add(sub, state_info)
                if state_info.job == 'udeleted':
                    self.block(sub, state_info)
            state_yaml = yaml.dump(self.state, sort_keys=False, allow_unicode=True)
            f.seek(0)
            f.write(state_yaml)
            f.truncate()

    def feed(self, sub, state_info):
        sub['etag'] = state_info.value.etag
        sub['modified'] = state_info.value.modified
        sub['image'] = state_info.value.image_href

    def remove(self, sub, state_info):
        for it in state_info:
            _dump = sub['current'].pop(it.guid)

    def add(self, sub, state_info):
        for it in state_info:
            sub['current'][it.guid] = {}
            sub['current'][it.guid]['path'] = it.path
            sub['current'][it.guid]['variables'] = it.variables

    def block(self, sub, state_info):
        for it in state_info:
            sub['blocked'].append(it.guid)
