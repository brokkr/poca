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
        <base_dir>/tmp/poca</base_dir>

        <!-- 
        The following settings relate to id3. These values are accepted:
        * id3encoding: utf8, latin1
        * id3removev1: yes, no -->

        <id3encoding>utf8</id3encoding>
        <id3removev1>yes</id3removev1>
    </settings>

    <subscriptions>

    <!-- Two podcasts are included to exemplify subscription configuration -->

        <subscription>
              <!-- The meaning of the subscription options are as follows:
            * title: The name used for the folder of the subscription and 
              for reference (required)
            * url: The address of the rss feed (required)
            * max_mb: The maximum disk space (in Mb) availlable to the 
              subscription. Any more than this will not be downloaded / be
              deleted (optional)
            * max_no: The maximum number of files to kepp in the 
              subscription. Any more than this will not be downloaded / be
              deleted. This can be used in conjunction with or instead of
              max_mb (optional) 
            * from_the_top: Default mode is to prioritise later episodes
              over newer, so if max_no is 4, poca will download the latest
              4 episodes. If from_the_top is set to 'yes' poca will instead
              start at the beginning, download the oldest four episodes. To
              move on to the next four, use 'poca --bump [title]'. This is 
              useful for audiobook-style podcasts or working your way through
              old episodes of a newly discovered podcast. (optional)
              -->

            <title>linux voice</title>
            <url>http://www.linuxvoice.com/podcast_mp3.rss</url>
            <max_no>150</max_no>
            <metadata>
                <!-- These settings will be used to overwrite the mp3 files'
                id3 metadata. The metadata tag and all subtags are optional. 
                All valid tags can be seen on the project wiki at
                https://github.com/brokkr/poca/wiki/ID3-frames -->

                <artist>Linux Voice</artist>
                <album>Linux Voice</album>
                <genre>podcast</genre>
            </metadata>
        </subscription>

        <subscription>
            <title>welcome to night vale</title>
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

