# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""poca.xml configuration template"""

from poco.outcome import Outcome


TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<poca version="0.7">

    <!-- Please see detailed configuration documentation online:
     https://github.com/brokkr/poca/wiki/Configuration -->

    <settings>

        <!-- The meaning of the settings options are briefly as follows:
        * base_dir: directory containing the individual subscription folders
        * id3encoding: encoding to use on metadata (utf8 or latin1)
        * id3removev1: should we remove id3v1, only keeping v2 (yes or no)
        * useragent: _fallback_ user agent if connection is rejected for
          default python user agent. Leave empty not to use a fallback.
        * email logging setup not included by default, see wiki for details.
        -->

        <base_dir>/tmp/poca</base_dir>
        <id3encoding>utf8</id3encoding>
        <id3removev1>yes</id3removev1>
        <useragent></useragent>

    </settings>

    <subscriptions>

        <!-- The meaning of the subscription options are brifly as follows:
        * title: Name used for the folder of the subscription (required)
        * url: The address of the rss feed (required)
        * max_number: Max number of files to keep in subscription (optional)
        * from_the_top: Get oldest files first, not newest (optional)
        * metadata: Override id3 header fields with these values
          (see https://github.com/brokkr/poca/wiki/ID3-frames for details)
        * filters: Contains one or more of following tags (all optional)
          * filename: Filename of the entry must match this string/regex
          * title: Same as above, only for the title in the rss 
          * hour: The hour (24h-format) at which the entry was published.
          * weekday: Only entries from one of these weekdays (as integers)
          * after_date: Only use entries published after date specified.
        -->

        <subscription>
            <title>example 1 - basic unlimited</title>
            <url>http://www.npr.org/rss/podcast.php?id=500005</url>
        </subscription>

        <subscription>
            <title>example 2 - start with the two oldest episodes</title>
            <url>http://nightvale.libsyn.com/rss</url>
            <max_number>2</max_number>
            <from_the_top>yes</from_the_top>
        </subscription>

        <subscription>
            <title>example 3 - override id3 header fields</title>
            <url>http://savagelove.savagelovecast.libsynpro.com/rss</url>
            <max_number>2</max_number>
            <metadata>
                <artist>Dan Savage</artist>
                <genre>podcast</genre>
            </metadata>
        </subscription>

        <subscription>
            <title>example 4 - filter based on weekday of publishing (only tuesdays)</title>
            <url>http://www.bbc.co.uk/programmes/p002vsnk/episodes/downloads.rss</url>
            <max_number>2</max_number>
            <filters>
                <weekday>1</weekday>
            </filters>
        </subscription>

    </subscriptions>

</poca>
"""

def write_template(file_path):
    '''Writes a string to file. Currently specific to creating config file.'''
    msg = 'No config file found. Writing one... \n'
    try:
        wfile = open(file_path, mode='wt', encoding='utf-8')
        wfile.write(TEMPLATE)
        wfile.close()
        msg = msg + file_path + ': Config template created.'
        return Outcome(True, msg)
    except IOError as e:
        msg = msg + file_path + ': ' + str(e)
        return Outcome(False, msg)
