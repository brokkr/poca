# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.


from poco.outcome import Outcome


template = """<?xml version="1.0" encoding="UTF-8"?>
<poca version="0.6">

    <!-- Please see detailed configuration documentation online:
     https://github.com/brokkr/poca/wiki/Configuration -->

    <settings>

        <!-- The meaning of the settings options are briefly as follows:
        * base_dir: directory containing the individual subscription folders
        * id3encoding: encoding to use on metadata (utf8 or latin1)
        * id3removev1: should we remove id3v1, only keeping v2 (yes or no)
        -->

        <base_dir>/tmp/poca</base_dir>
        <id3encoding>utf8</id3encoding>
        <id3removev1>yes</id3removev1>
    </settings>

    <subscriptions>

        <!-- The meaning of the subscription options are brifly as follows:
        * title: Name used for the folder of the subscription (required)
        * url: The address of the rss feed (required)
        * max_no: Max number of files to keep in subscription (optional)
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
            <title>example 1 - linux voice</title>
            <url>http://www.linuxvoice.com/podcast_mp3.rss</url>
            <max_no>4</max_no>
            <filters>
                <title>Season 4</title>
            </filters>
            <metadata>
                <artist>Linux Voice</artist>
                <album>Linux Voice</album>
                <genre>podcast</genre>
            </metadata>
        </subscription>

        <subscription>
            <title>example 2 - welcome to night vale</title>
            <url>http://nightvale.libsyn.com/rss</url>
            <max_no>5</max_no>
            <from_the_top>yes</from_the_top>
        </subscription>

    </subscriptions>

</poca>
"""

def write_template(file_path):
    '''Writes a string to file. Currently specific to creating config file.'''
    try:
        wfile = open(file_path, mode='wt', encoding='utf-8')
        wfile.write(template)
        wfile.close()
        return Outcome(True, file_path + ': Config template created.')
    except IOError as e:
        return Outcome(False, file_path + ': ' + str(e))

