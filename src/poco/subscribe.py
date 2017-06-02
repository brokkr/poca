#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Functions for subscription management for poca"""


from lxml import etree, objectify
from mutagen.easyid3 import EasyID3

from poco import files
from poco.feedstats import Feedstats


def search(xml, args):
    '''Takes a query and returns subscriptions with matching titles'''
    if args.title:
        search_tuple = ('title', args.title)
    elif args.url:
        search_tuple = ('url', args.url)
    else:
        return xml.xpath('./subscriptions/subscription')
    search_str = './subscriptions/subscription[contains(%s, "%s")]' % \
                 search_tuple
    results = xml.xpath(search_str)
    if not results:
        print("No titles match your query.")
    return results

def pretty_print(el):
    '''Debug helper function'''
    objectify.deannotate(el, cleanup_namespaces=True)
    pretty_xml = etree.tostring(el, encoding='unicode', pretty_print=True)
    return pretty_xml

def write(conf):
    '''Writes the resulting conf file back to poca.xml'''
    root_str = pretty_print(conf.xml)
    with open(conf.paths.config_file, 'w') as f:
        f.write(root_str)

def delete(conf, args):
    '''Remove xml subscription and delete audio and log files'''
    results = search(conf.xml, args)
    for result in results:
        verify = input("\"%s\" matches your query. "
                       "Remove subscription? (yes/no) " % result.title)
        if not verify or verify.lower() != 'yes':
            continue
        else:
            conf.xml.subscriptions.remove(result)
            files.delete_sub(conf, result.title.text, reset=True)
    write(conf)

def stats(conf, args):
    '''Remove xml subscription and delete audio and log files'''
    results = search(conf.xml, args)
    for result in results:
        result_stats = Feedstats(result.url.text)
        print(result.title.text.upper())
        result_stats.print_stats()
        print()
        _ = input("Enter to continue ")
        print()

def toggle(conf, args):
    '''Toggle subscription state between 'active' and 'inactive' '''
    results = search(conf.xml, args)
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
            files.delete_sub(conf, result.title.text)
    write(conf)

def user_input_add_sub():
    '''Get user input for new subscription'''
    sub_lst = ['title', 'url', 'max_number', 'from_the_top']
    sub_dic = dict.fromkeys(sub_lst)
    print("Press enter to skip setting (except * mandatory)")
    while not sub_dic['url']:
        sub_dic['url'] = input("* Url of subscription? ")
    url_stats = Feedstats(sub_dic['url'])
    url_stats.print_stats()
    title = input("Title of subscription? (Enter to use feed title) ")
    sub_dic['title'] = title if title else url_stats.title
    while True:
        max_number = input("Maximum number of files in subscription? "
                           "(integer/Enter to skip) ")
        if max_number:
            try:
                sub_dic['max_number'] = int(max_number)
                break
            except ValueError:
                pass
        else:
            break
    while sub_dic['from_the_top'] not in ['', 'yes', 'no']:
        sub_dic['from_the_top'] = input("Get earliest entries first? "
                                         "(yes/no/Enter to skip) ")
    sub_category = input("Category for subscription? ")
    print("To add metadata or filters settings, please edit poca.xml")
    sub_dic = {key: sub_dic[key] for key in sub_dic if sub_dic[key]}
    return (sub_dic, sub_category)

def add_sub(conf, sub_category, sub_dic):
    '''A quick and dirty add-a-sub function'''
    if conf.xml.find('subscriptions') is None:
        objectify.SubElement(conf.xml, "subscriptions")
    new_sub = objectify.SubElement(conf.xml.subscriptions, "subscription")
    if sub_category:
        new_sub.set('category', sub_category)
    for key in sub_dic:
        setattr(new_sub, key, sub_dic[key])
    write(conf)

def list_subs(conf):
    '''A simple columned output of subscriptions and their urls'''
    subs_lst = conf.xml.xpath('./subscriptions/subscription')
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
            title = sub.find('title') or '[no title]'
            title = str(title)[:30].ljust(32)
            state = sub.get('state') or 'active'
            state = state.ljust(10)
            max_no = sub.find('max_number') or ''
            max_no = str(max_no).ljust(8)
            url = str(sub.find('url') or '[no url]')
            print(title, state, max_no, url)
        print()

def list_id3_tags():
    valid_tags = list(EasyID3.valid_keys.keys())
    valid_tags.sort()
    for tag in valid_tags:
        print(tag)
