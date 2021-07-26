# -*- coding: utf-8 -*-

# Copyright 2010-2021 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Provides namedtuple used to return results of operations"""

from collections import namedtuple

Outcome = namedtuple('Outcome', 'success msg')
FeedStatus = namedtuple('FeedStatus',  ['http_code', 'new_url', 'exception',
                                        'image_href', 'etag', 'modified'])
StateInfo = namedtuple('StateInfo', ['title', 'job', 'value'])

