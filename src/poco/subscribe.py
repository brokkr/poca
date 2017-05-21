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


def search(root, search_tag, search_term):
    '''Takes a query and returns subscriptions with matching titles'''
    search_str = './subscriptions/subscription[contains(%s, "%s")]' % \
                 (search_tag, search_term)
    results = root.xpath(search_str)
    return results

def write(config):
    '''Writes the resulting config file back to poca.xml'''
    root_str = etree.tostring(config.xml, encoding='unicode',
                              pretty_print=True)
    with open(config.paths.config_file, 'w') as f:
        f.write(root_str)

def delete(config, args):
    '''Remove xml subscription and delete audio and log files'''
    if args.title:
        results = search(config.xml, 'title', args.title)
    elif args.url:
        results = search(config.xml, 'url', args.url)
    else:
        results = config.xml.subscriptions.xpath('./subscription')
    if not results:
        print("No titles match your query.")
        return
    for result in results:
        verify = input("\"%s\" matches your query. "
                       "Remove subscription (y/N)? " % result.title)
        if not verify or verify.lower() != 'y':
            continue
        else:
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

def user_input_add_sub():
    '''Get user input for new subscription'''
    sub_dic = {'title': '', 'url': ''}
    print("Press enter to skip setting (except * mandatory)")
    while not sub_dic['title']:
        sub_dic['title'] = input("* Title of subscription? ")
    while not sub_dic['url']:
        sub_dic['url'] = input("* Url of subscription? ")
    sub_dic['max_number'] = input("Maximum number of files in subscription? ")
    sub_dic['from_the_top'] = input("Get earliest entries first (yes/No)? ")
    sub_category = input("Category for subscription? ")
    print("To add metadata or filters settings, please edit poca.xml")
    sub_dic = {key: sub_dic[key] for key in sub_dic if sub_dic[key]}
    return (sub_dic, sub_category)

def add_sub(config, sub_category, sub_dic):
    '''A quick and dirty add-a-sub function'''
    new_sub = objectify.SubElement(config.xml.subscriptions, "subscription")
    if sub_category:
        new_sub.set('category', sub_category)
    for key in sub_dic:
        setattr(new_sub, key, sub_dic[key])
    objectify.deannotate(new_sub, cleanup_namespaces=True)
    write(config)

def list_subs(config):
    '''A simple columned output of subscriptions and their urls'''
    subs_lst = config.subs.xpath('./subscription')
    cats_dic = {sub.get('category'): [] for sub in subs_lst}
    for sub in subs_lst:
        cats_dic[sub.get('category')].append(sub)
    for key in cats_dic:
        if key:
            heading = key.upper()
        else:
            heading = 'NO CATEGORY'
        state = 'STATE'
        max_no = 'MAX NO'
        url = 'URL'
        print(heading.ljust(32), state.ljust(10), max_no.ljust(8), url)
        heading_line = ''.ljust(len(heading),'-').ljust(32)
        state_line = ''.ljust(5,'-').ljust(10)
        maxno_line = ''.ljust(6,'-').ljust(8)
        url_line = ''.ljust(3,'-')
        print(heading_line, state_line, maxno_line, url_line)
        for sub in cats_dic[key]:
            title = sub.title.text[:30].ljust(32)
            state = sub.get('state') or 'active'
            state = state.ljust(10)
            max_no = sub.find('max_number') or ''
            max_no = str(max_no).ljust(8)
            print(title, state, max_no, sub.url)
        print()

def toggle(config, args):
    '''Toggle subscription state between 'active' and 'inactive' '''
    if args.title:
        results = search(config.xml, 'title', args.title)
    elif args.url:
        results = search(config.xml, 'url', args.url)
    else:
        results = config.xml.subscriptions.xpath('./subscription')
    if not results:
        print("No titles match your query.")
    for result in results:
        state = result.get('state') if 'state' in result.attrib else 'active'
        state_input = input("%s is currently %s. Set to active (a) "
                            "or inactive (i)? " % (result.title.text, state))
        state_dic = {'a': 'active', 'i': 'inactive'}
        try:
            state = state_dic[state_input]
        except KeyError:
            continue
        result.set('state', state)
        if state_input == 'i':
            sub_dir = os.path.join(config.settings.base_dir.text,
                                   result.title.text)
            try:
                shutil.rmtree(sub_dir)
            except FileNotFoundError:
                pass
    write(config)