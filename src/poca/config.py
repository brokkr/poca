# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""A config parser using lxml objectify and XPath"""

from os import path
from lxml import etree, objectify
from copy import deepcopy

from poca import files, output, xmlconf
from poca.lxmlfuncs import merge
from poca.outcome import Outcome


E = objectify.ElementMaker(annotate=False)
DEFAULT_XML = E.poca(
                     E.settings(
                                E.base_dir('/tmp/poca'),
                                E.filenames('permissive', {'v0': 'permissive',
                                                           'v1': 'ntfs',
                                                           'v2': 'restrictive',
                                                           'v3': 'fallback'}),
                                E.id3v2version(4, {'v0': 3, 'v1': 4}),
                                E.id3removev1('yes', {'v0': 'yes',
                                                      'v1': 'no'}),
                                E.useragent(''),
                                E.email(
                                        E.only_errors('no', {'v0': 'yes',
                                                             'v1': 'no'}),
                                        E.threshold(1),
                                        E.host('localhost'),
                                        E.starttls('no', {'v0': 'yes',
                                                          'v1': 'no'}),
                                        E.password('')
                                       )
                               ),
                     E.defaults(),
                     E.subscriptions()
                     )


class Config:
    '''Collection of all configuration options'''
    def __init__(self, args, merge_default=False):
        self.args = args
        self.paths = Paths(args)
        if merge_default:
            objectify.deannotate(DEFAULT_XML)
            self.xml = deepcopy(DEFAULT_XML)
            user_xml = self.get_xml()
            errors = merge(user_xml, self.xml, DEFAULT_XML, errors=[])
            for outcome in errors:
                output.config_fatal(outcome.msg)
        else:
            self.xml = self.get_xml()
        base_dir = self.xml.settings.base_dir.text
        self.paths.test_base_dir(base_dir)

    def get_xml(self):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            with open(self.paths.config_file, 'r') as f:
                xml_object = objectify.parse(f)
            return xml_object.getroot()
        except etree.XMLSyntaxError as e:
            msg = 'Could not parse %s. Parser said:\n%s' % \
                (self.paths.config_file, str(e))
            output.config_fatal(msg)
        except PermissionError:
            msg = 'Could not read %s' % self.paths.config_file
            output.config_fatal(msg)


class Paths:
    '''A data-holder object for all program paths'''
    def __init__(self, args):
        if args.config:
            self.config_dir = self.expandall(args.config)
        else:
            self.config_dir = self.expandall(path.join('~', '.poca'))
        self.config_file = path.join(self.config_dir, 'poca.xml')
        self.db_dir = path.join(self.config_dir, 'db')
        self.log_file = path.join(self.config_dir, 'poca.log')
        self.test_paths(args)

    def expandall(self, _path):
        '''turn var into full absolute path'''
        _path = path.expandvars(path.expanduser(_path))
        _path = path.abspath(_path)
        return _path

    def test_paths(self, args):
        '''Checks for presence of ~/.poca/poca.xml. If that doesn't exist, try
        to create it. Also, check for existance of the db directory.'''
        if not path.isfile(self.config_file):
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

    def test_base_dir(self, base_dir):
        # test base_dir is writable
        self.base_dir = base_dir
        base_dir_outcome = files.check_path(self.base_dir)
        if not base_dir_outcome.success:
            output.config_fatal(base_dir_outcome.msg)

def subs(conf):
    xp_str = './subscription[not(@state="inactive")][title][url]'
    valid_subs = conf.xml.subscriptions.xpath(xp_str)
    valid_subs = [sub for sub in valid_subs if sub.title.text and sub.url.text]
    sub_names = [sub.title.text for sub in valid_subs]
    dupes = set([x for x in sub_names if sub_names.count(x) > 1])
    if len(dupes) > 0:
        msg = "Found the following duplicate titles: %s" % ', '.join(dupes)
        output.config_fatal(msg)
    return valid_subs
