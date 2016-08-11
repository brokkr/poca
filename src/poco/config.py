# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

from os import path
from sys import exit
import logging
from xml.etree import ElementTree 

from poco import files
from poco.xmlconf import template
from poco.output import add_filehandler


logger = logging.getLogger('POCA')

class Config:
    def __init__(self, args):
        '''Collection of all configuration options'''
        self.paths = Paths()
        self.args = args
        if self.args.logfile:
            add_filehandler(self.paths.log_file, logger)
        xml_root = self.get_xml()
        self.prefs = Prefs(xml_root)
        self.subs = get_subs(self.prefs, xml_root)

    def get_xml(self):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            return ElementTree.parse(self.paths.config_file).getroot()
        except ElementTree.ParseError as e:
            logger.error('The settings file could not be parsed.') 
            logger.error('Parser said: ' + str(e))
            exit()

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
                logger.error(outcome.msg)
                exit()
        if not path.isfile(self.config_file):
            outcome = files.write_file(self.config_file, template)
            if outcome.success:
                msg = [
                    'No config file found.', 
                    'New template config file created: ' + self.config_file,
                    'Please customize and run POCA again.'
                    ]
            else:
                msg = [
                    'No config file found.',
                    'Failed creating config file: ' + self.config_file
                    ]
            for line in msg:
                logger.error(line)
            exit()

class Prefs:
    def __init__(self, xml_root):
        '''Collection of global preferences, mainly base directory for mp3s'''
        xml_prefs = xml_root.find('settings')
        if xml_prefs is None:
            logger.error('No \'settings\' tag found. Quitting.')
            exit()
        required = {'id3removev1', 'id3version', 'id3unicode', 'base_dir'}
        elements = [ (e.tag, e.text) for e in xml_prefs.getchildren() ]
        missing_required = required - { e[0] for e in elements }
        if missing_required:
            logger.error('Missing required settings:' + list(missing_required))
            exit()
        for e in elements:
            setattr(self, e[0], e[1])

def get_subs(prefs, xml_root):
    '''Function to create a list of all subscriptions and their preferences'''
    xml_subs = xml_root.find('subscriptions')
    if xml_subs is None:
        logger.error('No \'subscriptions\' tag found. Quitting.')
        exit()
    else:
        return [ Sub(prefs, xml_sub) for xml_sub in xml_subs.getchildren() ]

class Sub:
    def __init__(self, prefs, xml_sub):
        '''Create a subscription object with metadata in dic if any'''
        self.metadata = None
        xml_meta = xml_sub.find('metadata')
        if xml_meta is not None:
            xml_sub.remove(xml_meta)
            self.metadata = { e.tag: e.text for e in xml_meta.getchildren() }
        required = {'title', 'url', 'max_mb'}
        elements = [ (e.tag, e.text) for e in xml_sub.getchildren() ]
        missing_required = required - { e[0] for e in elements }
        if missing_required:
            logger.error('A subscription is missing required settings: ' + 
                list(missing_required))
            exit()
        for e in elements:
            setattr(self, e[0], e[1])
        self.sub_dir = path.join(prefs.base_dir, self.title)
    
