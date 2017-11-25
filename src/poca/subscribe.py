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
import re
import fcntl
from lxml import etree, objectify
from mutagen.easyid3 import EasyID3
from argparse import Namespace

try:
    import audiosearch
except ImportError:
    audiosearch = None

from poca import files, output, config, outcome
from poca.lxmlfuncs import pretty_print
from poca.feedstats import Feedstats


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


def write(conf):
    '''Writes the resulting conf file back to poca.xml'''
    root_str = pretty_print(conf.xml)
    with open(conf.paths.config_file, 'r+') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            f.seek(0)
            f.truncate()
            f.write(root_str)
            fcntl.flock(f, fcntl.LOCK_UN)
            return outcome.Outcome(True, 'Config file updated')
        except BlockingIOError:
            return outcome.Outcome(False, 'Config file blocked')


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
    for index, result in enumerate(results):
        result_stats = Feedstats(result.url.text)
        print(result.title.text.upper())
        result_stats.print_stats()
        if index + 1 == len(results):
            return
        else:
            print()
            _ = input("Enter to continue ")
            print()


def toggle(conf, args):
    '''Toggle subscription state between 'active' and 'inactive' '''
    results = search(conf.xml, args)
    for result in results:
        state = result.get('state') if 'state' in result.attrib else 'active'
        state_input = input("%s is currently %s. Set to active (a) or inactive"
                            " (i)? " % (result.title.text, state.upper()))
        state_dic = {'a': 'active', 'i': 'inactive'}
        try:
            state = state_dic[state_input]
        except KeyError:
            continue
        result.set('state', state)
        if state_input == 'i':
            files.delete_sub(conf, result.title.text)
        write(conf)


def user_input_add_sub(url=None):
    '''Get user input for new subscription'''
    sub_lst = ['title', 'url', 'max_number', 'from_the_top']
    sub_dic = dict.fromkeys(sub_lst)
    if url is None:
        while not sub_dic['url']:
            sub_dic['url'] = input("Url of subscription: ")
    else:
        sub_dic['url'] = url
    print()
    url_stats = Feedstats(sub_dic['url'])
    url_stats.print_stats()
    print()
    title = input("Title of subscription: (Enter to use feed title) ")
    sub_dic['title'] = title if title else url_stats.title
    while True:
        max_number = input("Maximum number of files in subscription: "
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
        sub_dic['from_the_top'] = input("Get earliest entries first: "
                                        "(yes/no/Enter to skip) ")
        sub_category = input("Category for subscription: ")
    print("To add metadata, rename or filters settings, please edit poca.xml")
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
        heading_line = ''.ljust(len(heading), '-').ljust(32)
        state_line = ''.ljust(5, '-').ljust(10)
        maxno_line = ''.ljust(6, '-').ljust(8)
        url_line = ''.ljust(3, '-')
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
    '''list valid id3 tags to use in metadata overrides'''
    valid_tags = list(EasyID3.valid_keys.keys())
    valid_tags.sort()
    for tag in valid_tags:
        print(tag)


def search_show(conf, args):
    '''Search for show title on audiosear.ch'''
    oauth_id = conf.xml.find('./settings/audiosearch/id')
    oauth_secret = conf.xml.find('./settings/audiosearch/secret')
    if not audiosearch:
        msg = ("Missing audiosearch module. Please install with "
               "'pip3 install audiosearch'")
        output.subscribe_error(msg)
        return(None, None)
    if not oauth_id or not oauth_secret:
        msg = ("Missing audiosear.ch key and/or secret. "
               "Please get one at https://www.audiosear.ch/oauth/applications")
        output.subscribe_error(msg)
        return(None, None)
    try:
        client = audiosearch.client.Client(oauth_id, oauth_secret)
    except Exception as e:
        msg = "Audiosear.ch connection or authentication failed."
        output.subscribe_error(msg)
        return (None, None)
    if args.list_networks:
        networks = [network['name'].lower() for network in
                    client.get('/networks/')]
        networks.sort()
        for index, network in enumerate(networks):
            divisor, modulus = divmod(index, 20)
            if divisor > 0 and modulus == 0:
                print()
                _ = input('Press Enter to continue ')
                os.system('clear')
            print(network)
        return (None, None)
    search_dic = {'q': '*'}
    if args.keyword:
        search_dic['q'] = args.keyword
    if args.title:
        search_dic['q'] = "title:%s" % args.title
    if args.network:
        networks = [network['name'].lower() for network in
                    client.get('/networks/')]
        if args.network.lower() in networks:
            search_dic["filters[network.name]"] = args.network
        else:
            output.subscribe_info("Network not in audiosear.ch db. Run "
                                  "poca-subscribe search --list-networks for "
                                  "a list of known networks")
            return (None, None)
    search_query = client.search(search_dic, type='shows')
    results = search_query['results']
    for index, result in enumerate(results):
        title = result['title']
        desc_full = result['description'] if result['description'] else ''
        desc_start = re.match('[^\.\?\!]+', desc_full)
        desc = desc_start.group()[:77] if desc_start else ''
        network = result['network']['name'] if result['network'] else 'Unknown'
        print(index, title)
        print(' ', 'From:', network)
        print(' ', desc)
    no_search_results = len(results)
    if no_search_results == 0:
        output.subscribe_info('No results from search')
        return (None, None)
    select = input("Choose 0-%i: " % (no_search_results-1))
    try:
        choice = results[int(select)]
    except (ValueError, IndexError):
        return (None, None)
    return user_input_add_sub(url=choice['rss_url'])


def update_url(args, subdata):
    '''Used to implement 301 status code changes into conf'''
    pseudo_args = Namespace(title=subdata.sub.title, url=None)
    conf = config.Config(args, merge_default=False)
    sub = search(conf.xml, pseudo_args)[0]
    sub.url = subdata.new_url
    _outcome = write(conf)
    if _outcome.success is True:
        _outcome = outcome.Outcome(True, 'Have updated feed url to %s' %
                                   subdata.new_url)
    return _outcome
