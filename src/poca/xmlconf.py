# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""poca.xml configuration template"""

from lxml import objectify
from io import StringIO
from os import path

from poca.outcome import Outcome
from poca.lxmlfuncs import pretty_print


TEMPLATE = """<poca version="1.0">

  <!-- Please see detailed settings documentation online:
  https://github.com/brokkr/poca/wiki/Settings. The available
  options are briefly as follows:
  * base_dir: Directory containing the individual subscription folders
  * id3v2version: 3 for id3v2.3, 4 for id3v2.4 (default)
  * id3removev1: Should we remove id3v1, only keeping v2 (yes or no) -->

  <settings>
    <base_dir>/tmp/poca</base_dir>
    <id3v2version>4</id3v2version>
    <id3removev1>yes</id3removev1>
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

    <!-- This is an example for illustration purposes. Feel free to delete.
    <subscription>
      <title>Serial</title>
      <url>http://feeds.serialpodcast.org/serialpodcast?format=xml</url>
      <max_number>3</max_number>
      <metadata>
        <genre>Podcast</genre>
      </metadata>
    </subscription>
    -->

  </subscriptions>

</poca>
"""


def write_config_file(config_file_path):
    '''Writes default config xml to config file'''
    print("No config file found. Making one at %s." % config_file_path)
    default_base_dir = path.expanduser(path.join('~', 'poca'))
    query = input("Please enter the full path for placing media files.\n"
                  "Press Enter to use default (%s): " % default_base_dir)
    template_file = StringIO(TEMPLATE)
    config_xml = objectify.parse(template_file)
    config_root = config_xml.getroot()
    config_root.settings.base_dir = query if query else default_base_dir
    config_xml_str = pretty_print(config_xml)
    try:
        config_file = open(config_file_path, mode='wt', encoding='utf-8')
        config_file.write(config_xml_str)
        config_file.close()
        msg = ("Default config succesfully written to %s.\n"
               "Please edit or run 'poca-subscribe' to add subscriptions."
               % config_file_path)
        return Outcome(True, msg)
    except IOError as e:
        msg = "Failed writing config to %s.\nError: %s" % (config_file_path,
                                                           str(e))
        return Outcome(False, msg)
