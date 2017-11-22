# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.


from lxml import etree, objectify


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

def pretty_print(el):
    '''Debug helper function'''
    objectify.deannotate(el, cleanup_namespaces=True)
    pretty_xml = etree.tostring(el, encoding='unicode', pretty_print=True)
    return pretty_xml
