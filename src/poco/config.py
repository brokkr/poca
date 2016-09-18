# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import sys
import time
import logging
from os import path
from xml.etree import ElementTree 

from poco import files, output, xmlconf, plogging


logger = logging.getLogger('POCA')

class Config:
    def __init__(self, args):
        '''Collection of all configuration options'''
        self.paths = Paths()
        self.args = args
        if self.args.logfile:
            plogging.add_filehandler(self.paths.log_file, logger)
        xml_root = self.get_xml()
        self.prefs = Prefs(xml_root)
        self.subs = get_subs(self.prefs, xml_root)

    def get_xml(self):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            return ElementTree.parse(self.paths.config_file).getroot()
        except ElementTree.ParseError as e:
            msg = ('The settings file could not be parsed. \n' +
                'Parser said: ' + str(e))
            output.conffatal(msg)
            sys.exit()

class Paths:
    def __init__(self):
        '''Returns a dictionary with path settings'''
        self.config_dir = path.expanduser(path.join('~', '.poca'))
        self.config_file = path.join(self.config_dir, 'poca.xml')
        self.db_dir = path.join(self.config_dir, 'db')
        self.log_file = path.join(self.config_dir, 'poca.log')
        self.test_paths()

    def test_paths(self):
        '''Checks for presence of ~/.poca and ~/.poca/poca.xml'''
        for check_dir in [self.config_dir, self.db_dir]:
            outcome = files.check_path(check_dir)
            if not outcome.success:
                output.conffatal(outcome.msg)
                sys.exit()
        if not path.isfile(self.config_file):
            output.confinfo('No config file found. Writing one...')
            outcome = xmlconf.write_template(self.config_file)
            if outcome.success:
                output.confinfo(outcome.msg)
            else:
                output.conffatal(outcome.msg)
            sys.exit()

class Prefs:
    def __init__(self, xml_root):
        '''Collection of global preferences, mainly base directory for mp3s'''
        xml_prefs = xml_root.find('settings')
        if xml_prefs is None:
            msg = 'No \'settings\' tag found. Quitting.'
            output.conffatal(msg)
            sys.exit()
        required = {'id3removev1', 'id3encoding', 'base_dir'}
        elements = [ (e.tag, e.text) for e in xml_prefs.getchildren() ]
        missing_required = required - { e[0] for e in elements }
        if missing_required:
            msg = 'Missing required settings: ' + '\n'.join(missing_required)
            output.conffatal(msg)
            sys.exit()
        for e in elements:
            setattr(self, e[0], e[1])

def get_subs(prefs, xml_root):
    '''Function to create a list of all subscriptions and their preferences'''
    xml_subs = xml_root.find('subscriptions')
    if xml_subs is None:
        msg = 'No \'subscriptions\' tag found. Quitting.'
        output.conffatal(msg)
        sys.exit()
    else:
        return [ Sub(prefs, xml_sub) for xml_sub in xml_subs.getchildren() ]

class Sub:
    def __init__(self, prefs, xml_sub):
        '''Create a subscription object with metadata in dic if any'''
        self.metadata, self.filters = {}, {}
        xml_meta = xml_sub.find('metadata')
        if xml_meta is not None:
            xml_sub.remove(xml_meta)
            self.metadata = { e.tag: e.text for e in xml_meta.getchildren() }
        xml_filters  = xml_sub.find('filters')
        if xml_filters is not None:
            xml_sub.remove(xml_filters)
            self.filters = { e.tag: e.text for e in xml_filters.getchildren() }
            if 'after_date' in self.filters:
                self.filters['after_date'] = time.strptime(
                    self.filters['after_date'], "%Y-%m-%d")
        required = {'title', 'url'}
        elements = [ (e.tag, e.text) for e in xml_sub.getchildren() ]
        missing_required = required - { e[0] for e in elements }
        if missing_required:
            msg = ('A subscription is missing required settings: ' + 
                '\n'.join(missing_required))
            output.conffatal(msg)
            sys.exit()
        self.max_no = False
        for e in elements:
            setattr(self, e[0], e[1])
        self.sub_dir = path.join(prefs.base_dir, self.title)

    def __str__(self):
        '''String representation of object?'''
        return str(self.__dict__)

    def __ne__(self, other):
        '''Used to compare old sub instance to new to scan for changes'''
        return self.__dict__ != other.__dict__

