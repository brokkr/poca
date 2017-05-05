# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""A terrible, horrible, not good, very bad configuration parser"""

import sys
from os import path
from lxml import etree, objectify

from poco import files, output, xmlconf


SETTINGS = objectify.Element("settings")
DEFAULTS = objectify.Element("defaults")
E = objectify.E
DEFAULT_SETTINGS = E.root(E.base_dir('/tmp/poca'),
                          E.id3encoding('utf8'),
                          E.id3removev1('yes'),
                          E.useragent(''))

def confquit(msg):
    '''Something wasn't right about the preferences. Leave'''
    output.conffatal(msg)
    sys.exit()

class Config:
    '''Collection of all configuration options'''
    def __init__(self, args):
        self.paths = Paths(args)
        self.args = args
        xml_root = self.get_xml()
        self.xml = xml_root
        self.settings = DEFAULT_SETTINGS
        for element in xml_root.xpath('./settings/*'):
            self.settings[element.tag] = element
        defaults = xml_root.xpath('./defaults')
        self.defaults = defaults[0] if len(defaults) > 0 else DEFAULTS
        self.subs = xml_root.xpath('./subscriptions/subscription[title][url]')

    def get_xml(self):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            with open(self.paths.config_file, 'rb') as f:
                xml_object = objectify.parse(f)
            return xml_object.getroot()
        except etree.XMLSyntaxError as e:
            msg = ('The settings file could not be parsed. \n' +
                   'Parser said: ' + str(e))
            confquit(msg)

class Paths:
    '''Returns a dictionary with path settings'''
    def __init__(self, args):
        if args.config:
            self.config_dir = self.expandall(args.config)
        else:
            self.config_dir = self.expandall(path.join('~', '.poca'))
        self.config_file = path.join(self.config_dir, 'poca.xml')
        self.db_dir = path.join(self.config_dir, 'db')
        self.log_file = path.join(self.config_dir, 'poca.log')
        self.test_paths()

    def expandall(self, _path):
        '''turn var into full absolute path'''
        _path = path.expandvars(path.expanduser(_path))
        _path = path.abspath(_path)
        return _path

    def test_paths(self):
        '''Checks for presence of ~/.poca and ~/.poca/poca.xml'''
        for check_dir in [self.config_dir, self.db_dir]:
            outcome = files.check_path(check_dir)
            if not outcome.success:
                confquit(outcome.msg)
        if not path.isfile(self.config_file):
            outcome = xmlconf.write_template(self.config_file)
            confquit(outcome.msg)
