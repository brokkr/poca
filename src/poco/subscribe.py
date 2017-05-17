#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Functions for subscription management for poca"""

import os
import shutil
from lxml import etree, objectify


def search(root, search_term):
    '''Takes a query and returns subscriptions with matching titles'''
    search_str = './subscriptions/subscription[contains(title, "%s")]' % \
                 search_term
    results = root.xpath(search_str)
    return results

def delete(config, search_term):
    '''Remove xml subscription and delete audio and log files'''
    results = search(config.xml, search_term)
    if not results:
        print("No titles match your query.")
        return
    for result in results:
        verify = input("\"%s\" matches your query. "
                       "Remove subscription (Y/n)? " % result.title)
        if not verify or verify.lower() == 'y':
            config.xml.subscriptions.remove(result)
            sub_dir = os.path.join(config.settings.base_dir.text,
                                   result.title.text)
            db_file = os.path.join(config.paths.db_dir, result.title.text)
            try:
                shutil.rmtree(sub_dir)
                os.remove(db_file)
            except FileNotFoundError:
                pass
    write(config)

def add(config, title):
    '''A quick and dirty add-a-sub function'''
    new_sub = objectify.SubElement(config.xml.subscriptions, "subscription")
    setattr(new_sub, 'title', title)
    new_url = input("Please enter the url of \"%s\": " % title)
    setattr(new_sub, 'url', new_url)
    objectify.deannotate(new_sub, cleanup_namespaces=True)
    write(config)

def write(config):
    '''Writes the resulting config file back to poca.xml'''
    root_str = etree.tostring(config.xml, pretty_print=True)
    with open(config.paths.config_file, 'wb') as f:
        f.write(root_str)

