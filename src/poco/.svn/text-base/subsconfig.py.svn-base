# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.


import logging
from os.path import join 
import xml.etree.ElementTree as ElementTree

from poco import errors

def sets_n_subs(paths_dic):
    root = _get_tree_root(paths_dic)
    sets_dic = _get_settings(root)
    subs_list = _get_subscriptions(root, sets_dic)
    return (sets_dic, subs_list)

def _get_tree_root(paths_dic):
    '''Returns the XML tree root, harvested from the users poca.xml file.'''
    try:
        return ElementTree.parse(paths_dic['config_file']).getroot()
    except IOError:
        error = "POCA settings file missing. "
        suggest = ["Please add a poca.xml file to", 
            paths_dic['config_dir'],
            "or search your install for a poca.xml.example."]
        errors.errors(error, suggest, fatal=True)
    except ElementTree.ParseError:
        error = "The settings file could not be parsed. "
        suggest = ["Please check to see that it is wellformed etc."]
        errors.errors(error, suggest, fatal=True)

def _get_settings(xml_root):
    settings = xml_root.find('settings')
    metadata_sets_dic = _get_optional_branch(settings, 'metadata') 
    email_sets_dic = _get_optional_branch(settings, 'mail_account') 
    sets_dic = _dicify(settings)
    if metadata_sets_dic:
        sets_dic['metadata'] = metadata_sets_dic
    if email_sets_dic:
        sets_dic['mail_account'] = email_sets_dic
    if sets_dic.has_key('base_directory'):
        return sets_dic
    else:
        error = "Missing data in settings. "
        suggest = ["The base directory needs to be set in poca.xml."]
        errors.errors(error, suggest, fatal=True)

def _get_subscriptions(xml_root, sets_dic):
    subs_list = []
    subscriptions = xml_root.find('subscriptions')
    for subscription in subscriptions:
        metadata_dic = _get_optional_branch(subscription, 'metadata') 
        sub_dic = _dicify(subscription)
        if metadata_dic:
            sub_dic['metadata'] = metadata_dic
        try:
            sub_dic['sub_dir'] = join(sets_dic['base_directory'], sub_dic['title'])
            sub_dic['max_bytes'] = int(sub_dic['max_mb']) * 1024 * 1024
            sub_dic['url'] = sub_dic['url']
        except (AttributeError, TypeError, ValueError):
            error = "Wrong data type in subscription entry. Entry skipped. "
            suggest = ["Titles and URLs should be pure ASCII.",
                "Maximum MB should be given as an integer."]
            errors.errors(error, suggest, fatal=False)
            continue
        except KeyError:
            error = "Missing data in subscription entry. Entry skipped. "
            suggest = ["Please ensure that every entry has",
                "a <title>, a <url> and a <max_mb> tag."]
            errors.errors(error, suggest, fatal=False)
            continue
        subs_list.append(sub_dic)
    return subs_list

def _get_optional_branch(parent_node, child_title):
    '''Checks for an optional subbranch in parent node and if found, dicifies it'''
    opt_dic = {}
    child_node = parent_node.find(child_title)
    if child_node is not None:
        parent_node.remove(child_node)
        opt_dic = _dicify(child_node)
    return opt_dic

def _dicify(parent_node):
    '''Turns element to dictionary'''
    node_dic = {}
    for child_node in parent_node:
        node_dic[child_node.tag] = child_node.text
    return node_dic

