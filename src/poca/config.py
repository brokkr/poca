# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""A config parser using lxml objectify and XPath"""

from os import path
from pathlib import Path
from copy import deepcopy

from poca import files, output
from poca.outcome import Outcome


class Config:
    '''Collection of all configuration options'''
    def __init__(self, args, merge_default=False):
        self.args = args
        self.paths = Paths(args)
        # merge with default currently missing
        with self.config_file.open() as f:
            config_yaml = yaml.safe_load(f)
        # settings turned into attributes (KeyErrors anyone?)
        self.base_dir = Path(config_yaml['settings']['base_dir'])
        self.filenames = config_yaml['settings']['filenames']
        self.useragent = config_yaml['settings']['useragent']
        self.id3 = {'removev1': config_yaml['settings']['id3removev1'],
                    'v2version': config_yaml['settings']['id3version2']}
        base_dir_outcome = files.check_path(self.base_dir)
        if not base_dir_outcome.success:
            output.config_fatal(base_dir_outcome.msg)
        self.subs = config_yaml['subscriptions']

class Paths:
    '''A data-holder object for all program paths'''
    def __init__(self, args):
        if args.config:
            self.config_dir = Path(args.config)
        else:
            self.config_dir = Path.home().joinpath('.poca')
        self.config_file = self.config_dir.joinpath('poca.yaml')
        self.db_dir = self.config_dir.joinpath('db')
        self.log_file = self.config_dir.joinpath('poca.log')
        self.test_paths(args)

    def test_paths(self, args):
        '''Checks for presence of ~/.poca/poca.yaml. If that doesn't exist, try
        to create it. Also, check for existance of the db directory.'''
        # why arent' we
        # * first checking
        if not self.config_file.is_file():
            config_dir_outcome = files.check_path(self.config_dir)
            if not config_dir_outcome.success:
                output.config_fatal(config_dir_outcome.msg)
            config_file_outcome = xmlconf.write_config_file(self.config_file)
            output.config_fatal(config_file_outcome.msg)
        # test db_dir is writable
        db_dir_outcome = files.check_path(self.db_dir)
        if not db_dir_outcome.success:
            output.config_fatal(db_dir_outcome.msg)
        try:
            if args.logfile:
                logfile_outcome = files.check_file_write(self.log_file)
                if not logfile_outcome.success:
                    output.config_fatal(logfile_outcome.msg)
        # poca-subscribe does not have logfile as argument option
        except AttributeError:
            pass

def subs(conf):
    #valid_subs = conf.xml.subscriptions.xpath(xp_str)
    valid_subs = [sub for sub in valid_subs if sub.title.text and sub.url.text]
    sub_names = [sub.title.text for sub in valid_subs]
    dupes = set([x for x in sub_names if sub_names.count(x) > 1])
    if len(dupes) > 0:
        msg = "Found the following duplicate titles: %s" % ', '.join(dupes)
        output.config_fatal(msg)
    return valid_subs
