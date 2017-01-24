# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Read configuration from poca.xml"""

import sys
import time
import logging
from os import path
from xml.etree import ElementTree

from poco import files, output, xmlconf, plogging


STREAM = logging.getLogger('POCA')

def confquit(msg):
    '''Something wasn't right about the preferences. Leave'''
    output.conffatal(msg)
    sys.exit()

class Config:
    '''Collection of all configuration options'''
    def __init__(self, args):
        self.paths = Paths()
        self.args = args
        if self.args.logfile:
            plogging.add_filehandler(self.paths.log_file, STREAM)
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
            confquit(msg)

class Paths:
    '''Returns a dictionary with path settings'''
    def __init__(self):
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
                confquit(outcome.msg)
        if not path.isfile(self.config_file):
            output.confinfo('No config file found. Writing one...')
            outcome = xmlconf.write_template(self.config_file)
            confquit(outcome.msg)

class Prefs:
    '''Collection of global preferences, mainly base directory for mp3s'''
    def __init__(self, xml_root):
        xml_prefs = xml_root.find('settings')
        if xml_prefs is None:
            confquit('No \'settings\' tag found. Quitting.')
        required = {'id3removev1', 'id3encoding', 'base_dir'}
        elements = [(node.tag, node.text) for node in xml_prefs.getchildren()]
        missing_required = required - {element[0] for element in elements}
        if missing_required:
            confquit('Missing settings: ' + '\n'.join(missing_required))
        self.useragent = None
        for element in elements:
            setattr(self, element[0], element[1])


def get_subs(prefs, xml_root):
    '''Function to create a list of all subscriptions and their preferences'''
    xml_subs = xml_root.find('subscriptions')
    if xml_subs is None:
        msg = 'No \'subscriptions\' tag found. confquitting.'
        confquit(msg)
    else:
        return [Sub(prefs, xml_sub) for xml_sub in xml_subs.getchildren()]

class Sub:
    '''Create a subscription object with metadata in dic if any'''
    def __init__(self, prefs, xml_sub):
        self.metadata, self.filters = {}, {}
        self.set_metadata(xml_sub)
        self.set_filters(xml_sub)
        self.set_subsettings(xml_sub, prefs)

    def set_metadata(self, xml_sub):
        '''Saves settings about music file metadata'''
        xml_meta = xml_sub.find('metadata')
        if xml_meta is not None:
            xml_sub.remove(xml_meta)
            self.metadata = {e.tag: e.text for e in xml_meta.getchildren()}

    def set_filters(self, xml_sub):
        '''Saves settings about feed filters'''
        xml_filters = xml_sub.find('filters')
        if xml_filters is not None:
            xml_sub.remove(xml_filters)
            self.filters = {node.tag: node.text for node in
                            xml_filters.getchildren()}
            if 'after_date' in self.filters:
                self.filters['after_date'] = \
                    time.strptime(self.filters['after_date'], "%Y-%m-%d")

    def set_subsettings(self, xml_sub, prefs):
        '''Saves basic settings like title, url and max_number'''
        elements = [(x.tag, x.text) for x in xml_sub.getchildren()]
        if not 'url' in [x[0] for x in elements]:
            msg = 'A subscription is missing required url setting'
            confquit(msg)
        self.title = '__missing_title__'
        self.max_number = False
        for element in elements:
            setattr(self, element[0], element[1])
        self.sub_dir = path.join(prefs.base_dir, self.title)
        self.ctitle = self.title.upper()

    def __str__(self):
        '''String representation of object?'''
        return str(self.__dict__)

    def __ne__(self, other):
        '''Used to compare old sub instance to new to scan for changes'''
        return self.__dict__ != other.__dict__
