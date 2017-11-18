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
<poca version="1.0">

  <!-- Please see detailed settings documentation online:
  https://github.com/brokkr/poca/wiki/Settings. The available
  options are briefly as follows:
  * base_dir: Directory containing the individual subscription folders
  * id3v2version: 3 for id3v2.3, 4 for id3v2.4 (default)
  * id3removev1: Should we remove id3v1, only keeping v2 (yes or no)
  * useragent: Fallback user agent if connection is rejected for
    default python user agent. Leave empty not to use a fallback. -->

  <settings>
    <base_dir>/tmp/poca</base_dir>
    <id3v2version>4</id3v2version>
    <id3removev1>yes</id3removev1>
    <useragent></useragent>
  </settings>

  <!-- Defaults take the same options as any single subscription. A
  setting here, e.g. max_number, is applied to all subscriptions but
  always overruled by sub-specific settings. Non-overruling settings in
  metadata and filters are combined, e.g. a sub-specific 'artist' tag and
  a global 'genre' tag -->

  <defaults>
  </defaults>

  <subscriptions>

    <!-- Use 'poca-subscribe add' to quickly add new subscriptions.
    See https://github.com/brokkr/poca/wiki/Subscriptions for a
    full explanation of options. The meaning of the subscription
    options are briefly as follows:
    * title: Name used for the folder of the subscription (required)
    * url: The address of the rss feed (required)
    * max_number: Max number of files to keep in subscription (optional)
    * from_the_top: Get oldest files first, not newest (optional)
    * metadata: Contains one or more metadata overrides (optional)
      (run 'poca-subscribe tags' for a list of valid values)
    * filters: Contains one or more filters (all optional)
    * rename: Contains template for renaming audio files (optional) -->

    <subscription comment="This is an example for illustration purposes">
      <title>Serial</title>
      <url>http://feeds.serialpodcast.org/serialpodcast?format=xml</url>
      <max_number>3</max_number>
      <metadata>
        <genre>Podcast</genre>
      </metadata>
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
