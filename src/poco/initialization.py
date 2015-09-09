# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.

from os import path, makedirs
from sys import exit
from shutil import copyfile


config_example = '/etc/poca.example.xml'

def test_paths(paths_dic):
    '''Checks for presence of ~/.poca and ~/.poca/poca.xml'''
    msg = ['No config file found.', \
    'An example/template config file has been created for you:', \
    paths_dic['config_file'], \
    'Please edit it to suit your preferences and then run poca again.']
    if not path.isdir(paths_dic['config_dir']):
        makedirs(paths_dic['config_dir'])
    if path.isfile(paths_dic['config_file']):
        return 
    else:
        copyfile(config_example, paths_dic['config_file'])
        for line in msg: print line
        exit()

