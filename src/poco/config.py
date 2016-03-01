#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

from os import path, makedirs
from sys import exit
from shutil import copyfile
from xml.etree import ElementTree 

from poco import files


class Config:
    def __init__(self, args, out):
        self.paths = Paths()
        self.args = args
        xml_root = self.get_xml(out)
        self.prefs = Prefs(xml_root)
        self.subs = get_subs(self.prefs, xml_root)

    def get_xml(self, out):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            return ElementTree.parse(self.paths.config_file).getroot()
        except ParseError, e:
            out.single("The settings file could not be parsed. ")
            exit()

class Paths:
    def __init__(self):
        '''Returns a dictionary with path settings'''
        self.config_dir = path.expanduser(path.join('~', '.poca'))
        self.config_file = path.join(self.config_dir, 'poca.xml')
        self.db_dir = path.join(self.config_dir, 'db')
        self.history = path.join(self.config_dir, 'history.log')
        self.errors = path.join(self.config_dir, 'errors.log')

        self.test_paths()

    def test_paths(self):
        '''Checks for presence of ~/.poca and ~/.poca/poca.xml'''
        config_example = '/etc/poca.example.xml'
        msg = ['No config file found.', 
        'An example/template config file has been created for you:', 
        self.config_file, 
        'Please edit it to suit your preferences and then run poca again.']
        if not path.isdir(self.config_dir):
            makedirs(self.config_dir)
        if path.isfile(self.config_file):
            return 
        else:
            copyfile(config_example, self.config_file)
        for line in msg: 
            print line
            # This needs to make proper use of error logging functions
        exit()

class Prefs:
    def __init__(self, xml_root):
        xml_prefs = xml_root.find('settings')
        for element in xml_prefs.getchildren():
            setattr(self, element.tag, element.text)
        required = ['id3removev1', 'id3version', 'id3unicode', 'base_dir']
        try:
            for element in required:
                getattr(self, element)
        except AttributeError:
            print 'Yikes! Required setting is missing!'
            # This needs to make proper use of error logging functions
            exit()

def get_subs(prefs, xml_root):
    xml_subs = xml_root.find('subscriptions')
    if xml_subs is None:
        return []
    else:
        return [ Sub(prefs, xml_sub) for xml_sub in xml_subs.getchildren() ]

class Sub:
    def __init__(self, prefs, xml_sub):
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
        if xml_metadata is None:
            return metadata
        for element in xml_metadata.getchildren():
            metadata[element.tag] = element.text
        return metadata

