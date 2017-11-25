.. poca documentation master file, created by
   sphinx-quickstart on Fri Nov 24 09:28:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Poca
====

`Poca <https://projects.brokkr.net/projects/poca>`_ is a fast, multithreaded 
and highly customizable command line podcast client, written in Python 3. As 
of 1.0 all planned features have been implemented. 

.. contents::
   :depth: 2

Features
--------


* **Maximum amount.** Specify how many episodes the subscription should get 
  before deleting old episodes to make room for new ones.
* **Override ID3/Vorbis metadata.** If you want *Savage Love* to have *Dan 
  Savage* in the artist field (rather than *The Stranger*\ ), poca will 
  automatically update the metadata upon download of each new episode. Or set
  genre to be overwritten by *Podcast* as a default.
* **Filter a feed.** Only want news reports in the morning or on Wednesdays? 
  Use criteria such as filename and title, or the hour, weekday or date of 
  publishing to filter what you want from a feed.
* **Rename files automatically.** Not all feeds have sensibly named media 
  files. Specify a renaming template like date_title to know what you're
  dealing with or to get alphabetical ordering to match chronology.
* **From the top.** A latecomer to *Serial* or other audiobook style podcasts?
  Specify ``from_the_top`` to get  oldest episodes first, rather 
  than the latest. To move on to later episodes simply delete old ones and 
  poca will fill up with the next in line.
* **Keeping track.** Poca logs downloads and removals to a local file so you
  easily see what's changed. Or configure it with an SMTP server and get
  notified when a feed stops working.
* **Manage your shows** by editing an easy-to-understand xml file. Or use
  the accompanying tool to add, delete, sort them, or get info about their
  publishing frequency, average episode length and more.

Poca also: has excellent unicode support for feeds, filenames and tags, gets 
cover images for feeds, has the ability to spoof user agents, can pause your
subscriptions, deals intelligently with interruptions, updates moved feeds
(HTTP 301) automatically, and more.

Interface
---------


.. image:: https://asciinema.org/a/OScSRCdsKGZLntYJ9K6LYSNMT.png
   :target: https://asciinema.org/a/OScSRCdsKGZLntYJ9K6LYSNMT
   :alt: asciicast


All configuration is done in a single XML-format file. For cron job 
compatibility, Poca has a quiet mode in addition to normal and verbose.

Installation
------------

You can install poca from `pypi <https://pypi.python.org/pypi/poca>`_ using
pip. Be mindful that poca is python 3 so use ``pip3``\ :

.. code-block:: none

    pip3 install poca


To remove Poca - having installed it using pip - simply do:

.. code-block:: none

    pip3 uninstall poca


Quickstart
----------

.. code-block:: none

    [ ~ ] poca
    No config file found. Making one at /home/user/.poca/poca.xml.
    Please enter the full path for placing media files.
    Press Enter to use default (/home/user/poca): /tmp/poca
     ⚠ Default config succesfully written to /home/user/.poca/poca.xml.
    Please edit or run 'poca-subscribe' to add subscriptions.

    [ ~ ] poca-subscribe add
    Url of subscription: http://crateandcrowbar.com/feed/

    Author: The Crate and Crowbar                            PUBLISHED / 5 WEEKS
    Title:  The Crate and Crowbar

    Last episode: Episode 216: Videocrates Crowdog                       ▮
    Published:    24 Nov 2017                                            ▮
                                                                         ▮     ▮
    Avg. size of episode:   52 Mb                            ▮  ▮     ▮  ▮  ▮  ▮
    Avg. length of episode: 1h 52m                           M  T  W  T  F  S  S

    Title of subscription: (Enter to use feed title)
    Maximum number of files in subscription: (integer/Enter to skip) 5
    Get earliest entries first: (yes/no/Enter to skip) no
    Category for subscription (Enter to skip): gaming
    To add metadata, rename or filters settings, please edit poca.xml

    [ ~ ] poca --verbose
    THE CRATE AND CROWBAR. 5 ➕
     ⇵ CCEp214.mp3  [56 Mb]
     ⇵ LGCEp004.mp3  [35 Mb]
     ⇵ CCEp215.mp3  [61 Mb]
     ...


Configuration
-------------

The ``poca.xml`` file contains all poca's general and subscription specific 
configuration. To get started simply run ``poca`` once to get a basic config 
file placed in ``~/.poca``. 

The configuration file is divided into three main parts:

.. code-block:: xml

    <poca version="1.0">
      <settings>
      ...
      </settings>
      <defaults>
      ...
      </defaults>
      <subscriptions>
      ...
      </subscriptions>
    </poca>


* **Settings**: Contains general settings
* **Subscriptions**: Contains a list of all the podcasts you want to subscribe 
  to
* **Defaults**: Options in ``defaults`` are similar to those in 
  ``subscriptions``, only they apply globally (unless overridden).

.. toctree::
   :maxdepth: 2

   Settings
   Subscriptions


Running
-------

Poca is run by issuing the ``poca`` command. Subscriptions can be managed 
by using the helper script ``poca-subscribe``.

.. toctree::
   :maxdepth: 2

   poca
   poca-subscribe

Changelog
---------


Version `1.0 <https://github.com/brokkr/poca/issues?q=is%3Aopen+is%3Aissue+milestone%3A1.0>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added file renaming options (\ `#16 <https://github.com/brokkr/poca/issues/16>`_\ )
* More consistent output in normal and verbose mode
* audiosearch api removed again due to service closure (\ `#87 <https://github.com/brokkr/poca/issues/87>`_\ )
* Bugfixes, quibbles and niggles aplenty

Version `0.9 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.9>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Artificial track numbers (\ `#43 <https://github.com/brokkr/poca/issues/43>`_\ )
* Support for tagging with other formats than mp3: Ogg, opus, mp4, flac, ... (\ `#18 <https://github.com/brokkr/poca/issues/18>`_\ )
* Reintroduced support for id3v2.3
* poca-subscribe search: Seach for shows with audiosearch's api
* 'Preview' feed in poca-subscribe's add command (\ `#55 <https://github.com/brokkr/poca/issues/55>`_\ )
* Multithreading support with option for concurrent downloads as well as concurrent updates (\ `#45 <https://github.com/brokkr/poca/issues/45>`_\ )
* Subscription URLs are automatically updated when feeds move (HTTP status code 301)
* New dependency: ``requests`` for downloads due to downloading in threads

Version `0.8 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.8>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* New dependency: ``lxml`` for greatly simplified configuration parsing
* System defaults in case of missing or bad config and user set global subscription defaults
* New script: ``poca-subscribe``, a cli tool to manage subscriptions

Version `0.7 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.7>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Log: Terse logging (skip writing about subscription if nothing has changed) (\ `#32 <https://github.com/brokkr/poca/issues/32>`_\ )
* Email logging: A sensible email logging system (\ `#26 <https://github.com/brokkr/poca/issues/26>`_\ )
* Style: Investigating Syntastic complaints (\ `#39 <https://github.com/brokkr/poca/issues/39>`_\ )
* Bug fix: Hangs on feeds without entry size info (\ `#40 <https://github.com/brokkr/poca/issues/40>`_\ )
* Bug fix: Crash on entries without enclosures (\ `#41 <https://github.com/brokkr/poca/issues/41>`_\ )

Version `0.6 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.6>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* ``max_number``: Limit by number of files (\ `#14 </brokkr/poca/issues/14>`_\ )
* ``max_mb`` has been deprecated in favour of ``max_number``
* ``filters``: Filter entries by filename, date, ... (\ `#29 </brokkr/poca/issues/29>`_\ )
* ``from_the_top``: Option to start podcast from the beginning (\ `#28 </brokkr/poca/issues/28>`_\ )
* Download cover image from feed (\ `#25 </brokkr/poca/issues/25>`_\ )
* Testing for unicode exceptions in feed treatment and mp3 metadata (\ `#17 </brokkr/poca/issues/17>`_\ )
* Spoofed ``useragent`` introduced as fallback if urllib is denied


Version 0.5
^^^^^^^^^^^


* Completed port to Python 3
* Completely revised and simplified stream and log output
* Mp3 tagging reimplemented
* New download function with proper timeouts

Version 0.4
^^^^^^^^^^^


* Reduced functionality port to Python3
