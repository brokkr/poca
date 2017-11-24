
Poca
----

Poca is a fast, multithreaded and highly customizable command line podcast 
client, written in Python 3. As of 1.0 all planned features have been 
implemented.

Upgrade to 1.0 note
^^^^^^^^^^^^^^^^^^^

The 1.0 database is NOT backwards compatible. If you're upgrading to 1.0 
from any release prior to ``1.0beta4`` you will need to delete your media files 
and db folder. The ``db`` folder can be found in the config directory 
(\ ``~/.poca/db`` by default). The media files are in the folder designated by 
the ``base_dir`` setting in poca.xml. 

Older versions of ``poca.xml`` will work with 1.0 but be aware that new options
have been added and others deprecated. See 
`Settings <https://github.com/brokkr/poca/wiki/Settings>`_ for 
details.

Features
^^^^^^^^

Poca allows both for options for each individual subscription and
global defaults that apply to every subscription.


* **Maximum amount.** Specify how many episodes the subscription should get 
  before deleting old episodes to make room for new ones.
* **Override ID3/Vorbis metadata.** If you want *Savage Love* to have *Dan 
  Savage* in the artist field (rather than *The Stranger*\ ), poca will 
  automatically update the metadata upon download of each new episode. Set
  'genre' to be overwritten by 'Podcast' as a default. Or have poca add track
  numbers to shows that have left them out.
* **Filter a feed.** Only want news reports in the morning or on Wednesdays? 
  Use criteria such as filename and title, or the hour, weekday or date of 
  publishing to filter what you want from a feed.
* **Rename files automatically.** Not all feeds have sensibly named media 
  files. Specify a renaming template like date_title to know what you're
  dealing with or to get alphabetical ordering to match chronology.
* **From the top.** A latecomer to *Serial* or other audiobook style podcasts?
  Poca introduces a special mode that gets the oldest episodes first, rather 
  than the latest. To move on to later episodes simply delete old ones and 
  poca will fill up with the next in line.
* **Keeping track.** Poca logs downloads and removals to a local file so you
  easily see what's changed. Or configure it with an SMTP server and get
  notified when a feed stops working.
* **Manage your shows.** by editing an easy-to-understand xml file. Or use
  the accompanying tool to add, delete, sort them, or get info about their
  publishing frequency, average episode length and more.

Poca also: has excellent unicode support for feeds, filenames and tags, gets 
cover images for feeds, has the ability to spoof user agents, can pause your
subscriptions, deals intelligently with interruptions, updates moved feeds
(HTTP 301) automatically, and more.

See the `Configuration <https://github.com/brokkr/poca/wiki/Configuration>`_ 
section of the wiki for more details on features.

Interface
^^^^^^^^^


.. image:: https://asciinema.org/a/OScSRCdsKGZLntYJ9K6LYSNMT.png
   :target: https://asciinema.org/a/OScSRCdsKGZLntYJ9K6LYSNMT
   :alt: asciicast


All configuration is done in a single XML-format file. For cron job 
compatibility, Poca has a quiet mode in addition to normal and verbose.

Installing
^^^^^^^^^^

You can install poca from `pypi <https://pypi.python.org/pypi/poca>`_ using
pip. Be mindful that poca is python 3 so use ``pip3``\ :

.. code-block:: none

   pip3 install poca


To remove Poca - having installed it using pip - simply do:

.. code-block:: none

   pip3 uninstall poca



Dependencies
^^^^^^^^^^^^


* Python 3.4 or later is required
* A terminal capable of unicode output is recommended
* The following third-party modules are required: ``feedparser`` ``lxml`` ``mutagen`` ``requests``
* Pip will automatically install any one of these found missing
