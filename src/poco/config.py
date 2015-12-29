#!/usr/bin/env python2
# 
# Copyright 2010-2015 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import argparse

from os import path, makedirs
from sys import exit
from shutil import copyfile
from xml.etree import ElementTree 

from poco import VERSION, DESCRIPTION


class Config:
    def __init__(self):
        self.paths = Paths()
        self.args = get_args()
        xml_root = self.get_xml()
        self.prefs = Prefs(xml_root)
        self.subs = get_subs(xml_root)

    def get_xml(self):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            return ElementTree.parse(self.paths.config_file).getroot()
        except ElementTree.ParseError:
            error = "The settings file could not be parsed. "
            suggest = ["Please check to see that it is wellformed etc."]
            #errors.errors(error, suggest, fatal=True)
            print error

class Paths:
    def __init__(self):
        '''Returns a dictionary with path settings'''
        self.config_dir = path.expanduser(path.join('~', '.poca'))
        self.config_file = path.join(self.config_dir, 'poca.xml')
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

def get_subs(xml_root):
    subslist = []
    xml_subs = xml_root.find('subscriptions')
    if xml_subs is None:
        return subslist
    for xml_sub in xml_subs.getchildren():
        sub = Sub(xml_sub)
        subslist.append(sub)
    return subslist

class Sub:
    def __init__(self, xml_sub):
        xml_metadata = xml_sub.find('metadata')
        self.metadata = self.extract_metadata(xml_metadata)
        if xml_metadata is not None:
            xml_sub.remove(xml_metadata)
        for element in xml_sub.getchildren():
            setattr(self, element.tag, element.text)
            # test if all required attributes are set (and valid?)
    
    def extract_metadata(self, xml_metadata):
        metadata = {}
        if xml_metadata is None:
            return metadata
        for element in xml_metadata.getchildren():
            metadata[element.tag] = element.text
        return metadata

def get_args():
    '''Returns arguments from a command line argument parser'''
    about = "Poca " + VERSION + " : " + DESCRIPTION
    parser = argparse.ArgumentParser(description=about)

    parser.add_argument('-q', '--quiet', action='store_true', 
        default=False, help='Quiet mode (useful for cron jobs)')
    parser.add_argument('-e', '--log-errors', action='store_true', 
        default=False, help='Log errors to file in poca config directory')
    parser.add_argument('-r', '--restart', action='store_true', 
        default=False, help=('Delete all created directories with contents '
        'plus log file and start over'))

    return parser.parse_args()

