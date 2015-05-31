# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.

from os import path


def paths_config():
    '''Returns a dictionary with path settings'''
    paths_dic = {}
    paths_dic['config_dir'] = path.expanduser(path.join('~', '.poca'))
    paths_dic['history_log'] = path.join(paths_dic['config_dir'], 'history.sqlite')
    paths_dic['errors_log'] = path.join(paths_dic['config_dir'], 'errors.log')
    paths_dic['config_file'] = path.join(paths_dic['config_dir'], 'poca.xml')
    return paths_dic

