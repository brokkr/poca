# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""A config parser using lxml objectify and XPath"""

from os import path
from lxml import etree, objectify
from copy import deepcopy

from poco import files, output, xmlconf
from poco.outcome import Outcome


E = objectify.E
DEFAULT_XML = E.poca(
                     E.settings(
                                E.base_dir('/tmp/poca'),
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

def merge(user_el, new_el, default_el, errors=[]):
    '''Updating one lxml objectify elements with another
       (with primitive validation)'''
    for child in user_el.iterchildren():
        new_child = new_el.find(child.tag)
        default_child = default_el.find(child.tag)
        if default_child is None:
            new_el.append(child)
            continue
        if isinstance(child, objectify.ObjectifiedDataElement):
            right_type = type(child) == type(default_child)
            valid = child.text in default_child.attrib.values() \
                    if default_child.attrib else True
            if all((right_type, valid)):
                new_el.replace(new_child, child)
            else:
                errors.append(Outcome(False, '%s: %s. Value not valid'
                                      % (child.tag, child.text)))
        elif isinstance(child, objectify.ObjectifiedElement):
            merge(child, new_child, default_child, errors=errors)
    return errors

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
                output.config_fatal(msg)
        if not path.isfile(self.config_file):
            outcome = xmlconf.write_template(self.config_file)
            output.config_fatal(msg)

class Sub:
    '''Legacy class to avoid breakage with old saved subs'''
    pass

class Prefs:
    '''Legacy class to avoid breakage with old saved subs'''
    pass
