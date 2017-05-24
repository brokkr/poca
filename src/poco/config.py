# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""A config parser using lxml objectify and XPath"""

import sys
from os import path
from lxml import etree, objectify
from copy import deepcopy

from poco import files, output, xmlconf


E = objectify.E
DEFAULT_XML = E.poca(
                     E.settings(
                                E.base_dir('/tmp/poca'),
                                E.id3encoding('utf8'),
                                E.id3removev1('yes'),
                                E.useragent(''),
                                E.email(
                                        E.only_errors('no'),
                                        E.threshold(1),
                                        E.host('localhost'),
                                        E.starttls('no')
                                       )
                               ),
                      E.defaults(),
                      E.subscriptions()
                     )

def confquit(msg):
    '''Something wasn't right about the preferences. Leave'''
    output.conffatal(msg)
    sys.exit()

def merge(user_el, new_el, default_el):
   '''Updating one lxml objectify elements with another'''
   for child in user_el.iterchildren():
       new_child = new_el.find(child.tag)
       default_child = default_el.find(child.tag)
       if default_child is None:
           new_el.append(child)
           continue
       if isinstance(child, objectify.ObjectifiedDataElement):
           new_el.replace(new_child, child)
       elif isinstance(child, objectify.ObjectifiedElement):
           merge(child, new_child, default_child)

def pretty_print(el):
    '''Debug helper function'''
    objectify.deannotate(el, cleanup_namespaces=True)
    pretty_xml = etree.tostring(el, encoding='unicode', pretty_print=True)
    print(pretty_xml)

class Config:
    '''Collection of all configuration options'''
    def __init__(self, args):
        self.args = args
        self.paths = Paths(args)
        self.xml = deepcopy(DEFAULT_XML)
        user_xml = self.get_xml()
        merge(user_xml, self.xml, DEFAULT_XML)

    def get_xml(self):
        '''Returns the XML tree root harvested from the users poca.xml file.'''
        try:
            with open(self.paths.config_file, 'r') as f:
                xml_object = objectify.parse(f)
            return xml_object.getroot()
        except etree.XMLSyntaxError as e:
            msg = ('The settings file could not be parsed. \n' +
                   'Parser said: ' + str(e))
            confquit(msg)

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

class Sub:
    '''Legacy class to avoid breakage with old saved subs'''
    pass

class Prefs:
    '''Legacy class to avoid breakage with old saved subs'''
    pass
