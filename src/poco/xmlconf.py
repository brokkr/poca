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
            * max_no: The maximum number of files to kepp in the 
              subscription. Any more than this will not be downloaded / be
              deleted. This can be used in conjunction with or instead of
              max_mb (optional) 
            * from_the_top: Default mode is to prioritise later episodes
              over newer, so if max_no is 4, poca will download the latest
              4 episodes. If from_the_top is set to 'yes' poca will instead
              start at the beginning, download the oldest four episodes. To
              move on, simply delete old files and poca will get newer ones
              (still from the beginning) instead. This is useful for audio-
              book-style podcasts or working your way through old episodes of 
              a newly discovered podcast. (optional)
            * filters: contains one or more of the following tags that filter 
              filter the entries in the feed (optional). Note: Examples are
              written with square brackets to avoid closing off the comment.
              * filename: The filename of the entry must match this string 
                (or regex) in order to be included. Note that the tag is 
                interpreted as a regex, so certain characters should be 
                escaped (e.g. a literal point should be written '\.')
                Example: [filename]\.mp3[/filename] excludes the videos from
                         Ricky Gervais' podcast.
              * title: The same as above, only for the title in the rss 
                feed (not in the music file's metadata)
                Example: [title]Wires[/title] only gets the 'Within the Wires'
                         episodes from the Welcome to Nightvale feed.
              * hour: The hour (24h-format) at which the entry was published.
                This is useful for podcasts that put out more episodes a day
                than you need, e.g. news broadcasts. 
                Example: [hour]21[/hour] only gives you the evening edition
                         of BBC's Newshour.
              * weekday: Excludes all episodes not published on the specified
                weekdays. Each weekday to be included is written as a single
                digit where Monday is 0, Tuesday is 1, etc, up to 6 for 
                Sunday. 
                Example: [weekday]024[/weekday] to get Monday, Wednesday, 
                         and Friday episodes.
              * after_date: Excludes all episodes published BEFORE the date
                specified. Format is YYYY-MM-DD. This is useful is you want
                to assign lots of space to the sub but not download the back 
                catalogue.
                Example: [after_date]2016-08-23[/after_date]
              -->

            <title>linux voice</title>
            <url>http://www.linuxvoice.com/podcast_mp3.rss</url>
            <max_no>4</max_no>
            <filters>
                <title>Season 4</title>
            </filters>
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

