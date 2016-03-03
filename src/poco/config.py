# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

from os import path, makedirs
from sys import exit
from xml.etree import ElementTree 

from poco import files
from poco.xmlconf import template


class Config:
    def __init__(self, args, put):
        self.paths = Paths(put)
        self.args = args
        if self.args.logfile:
            put.add_filehandler(self.paths.log_file)
        xml_root = self.get_xml(put)
        self.prefs = Prefs(xml_root, put)
        self.subs = get_subs(self.prefs, xml_root, put)

    def get_xml(self, put):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            return ElementTree.parse(self.paths.config_file).getroot()
        except ElementTree.ParseError, e:
            put.multi(['The settings file could not be parsed. ', 
            'Parser said: ' + '\"' + e.message.message + '\"'])
            exit()

class Paths:
    def __init__(self, put):
        '''Returns a dictionary with path settings'''
        self.config_dir = path.expanduser(path.join('~', '.poca'))
        self.config_file = path.join(self.config_dir, 'poca.xml')
        self.db_dir = path.join(self.config_dir, 'db')
        self.log_file = path.join(self.config_dir, 'poca.log')
        self.test_paths(put)

    def test_paths(self, put):
        '''Checks for presence of ~/.poca and ~/.poca/poca.xml'''
        outcome = files.check_path(self.config_dir)
        if not outcome.success:
            put.single(outcome.msg)
            exit()
        if not path.isfile(self.config_file):
            outcome = files.write_file(self.config_file, template)
            if outcome.success:
                msg = ['No config file found. An example/template config file '
                'has been created for you:', ' ' + self.config_file, 'Please '
                'edit it to suit your preferences and then run poca again.']
            else:
                msg = ['No config file found. New config file could not be \
                written. Quitting.']
            put.multi(msg)
            exit()

class Prefs:
    def __init__(self, xml_root, put):
        xml_prefs = xml_root.find('settings')
        for element in xml_prefs.getchildren():
            setattr(self, element.tag, element.text)
        required = ['id3removev1', 'id3version', 'id3unicode', 'base_dir']
        try:
            for element in required:
                getattr(self, element)
        except AttributeError, e:
            put.single('Required setting is missing. Quitting.')
            exit()

def get_subs(prefs, xml_root, put):
    xml_subs = xml_root.find('subscriptions')
    if xml_subs is None:
        put.single('No subscriptions found. Quitting.')
        exit()
    else:
        return [ Sub(prefs, xml_sub, put) for xml_sub in xml_subs.getchildren() ]

class Sub:
    def __init__(self, prefs, xml_sub, put):
        xml_metadata = xml_sub.find('metadata')
        self.metadata = self.extract_metadata(xml_metadata)
        if xml_metadata is not None:
            xml_sub.remove(xml_metadata)
        for element in xml_sub.getchildren():
            setattr(self, element.tag, element.text)
            # test if all required attributes are set (and valid?)
        self.sub_dir = path.join(prefs.base_dir, self.title)
    
    def extract_metadata(self, xml_metadata):
        metadata = {}
        if xml_metadata is not None:
            for element in xml_metadata.getchildren():
                metadata[element.tag] = element.text
        return metadata

