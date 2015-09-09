# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.


import shelve


def retrieve(paths_dic, sub_dic):
    '''Retrieves the saved entries for the subscription in question'''
    log = shelve.open(paths_dic['history_log'])
    try:
        return log[sub_dic['title']]
    except KeyError:
        return
    finally:
        log.close()

def save(paths_dic, sub_dic, new_log):
    '''Opens log and saves updated entries the for subscription in question'''
    log = shelve.open(paths_dic['history_log'])
    log[sub_dic['title']] = new_log
    log.close()

