# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

template = """<?xml version="1.0" encoding="UTF-8"?>
<poca version="0.4">

    <!-- Please see detailed configuration documentation online:
     https://github.com/brokkr/poca/wiki/Configuration -->

    <settings>

        <base_dir>/tmp/poca</base_dir>

        <!-- NOT CURRENTLY IN USE! 
        The following settings relate to id3. These values are accepted:
        * id3version: 2.3, 2.4
        * id3unicode: yes (use utf16 encoding with 2.3, utf8 encoding with 2.4), 
          no (use latin1 encoding)
        * id3removev1: yes, no -->

        <id3version>2.3</id3version>
        <id3unicode>yes</id3unicode>
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

                <!-- NOT CURRENTLY IN USE! 
                These settings will be used to overwrite the mp3 file's
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

