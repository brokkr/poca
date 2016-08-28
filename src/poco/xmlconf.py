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
<poca version="0.5">

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

    <!-- a single podcast included to exemplify subscription configuration -->

        <subscription>

            <!-- The meaning of the subscription options are as follows:
            * title: the name used for the folder of the subscription
            * url: the address of the rss feed
            * max_mb: the maximum disk space (in Mb) availlable to the 
              subscription. Any more than this will not be downloaded / be
              deleted. -->

            <title>Linux Voice</title>
            <url>http://www.linuxvoice.com/podcast_mp3.rss</url>
            <max_mb>150</max_mb>
            <metadata>

                <!-- These settings will be used to overwrite the mp3 file's
                id3 metadata. The metadata tag and all subtags are optional. 
                All valid tags can be seen on the project wiki at
                https://github.com/brokkr/poca/wiki/ID3-frames -->

                <artist>Linux Voice</artist>
                <album>Linux Voice</album>
                <genre>podcast</genre>

            </metadata>

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

