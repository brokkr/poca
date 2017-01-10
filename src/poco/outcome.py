# -*- coding: utf-8 -*-

# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Provides class used to return results of operations"""

class Outcome:
    '''A way to return outcome of operations in a uniform fashion'''
    def __init__(self, success, msg=''):
        self.success = success
        self.msg = msg
