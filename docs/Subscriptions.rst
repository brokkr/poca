Subscriptions
=============

Subscriptions are podcast feeds you want poca to follow and (usually) 
download any new entries from. You create a subscription in poca by adding an 
xml ``subscription`` element with all the relevant settings to your 
``poca.xml`` configuration file. Using the add command from 
:doc:`poca-subscribe` is a nice shortcut if you don't like editing xml.

.. contents::

Structure
---------

Each ``<subscription>`` is created as an element under the 
``<subscriptions>`` element. The structure of a subscription element is as follows:

.. code-block:: xml

   <subscription category="..." state="...">
       <title>...</title>
       <url>...</url>
       <max_number>...</max_number>
       <from_the_top>...</from_the_top>
       <track_numbering>...</track_numbering>
       <metadata>
           <headerfield1>...</headerfield1>
           <headerfield2>...</headerfield2>
           <headerfield3>...</headerfield3>
       </metadata>
       <rename divider="..." space="...">
           <title/>
           <episode_title/>
           <date/>
           <uid/>
           <org_name/>
       </rename>
       <filters>
           <filename>...</filename>
           <title>...</title>
           <weekday>...</weekday>
           <hour>...</hour>
           <after_date>...</after_date>
       </filters>
   </subscription>


Required elements
-----------------

``subscription`` entries without the required elements are silently skipped 
during updates.

title
^^^^^

Title of show/subscription. Used only to name the subscription subdirectory 
under the **base_dir**\ , not to insert into ID3 headers. 

Before attempting to download files for a subscription, poca checks to see if
the subscription subdirectory exists and the user has permission to write to
it. If not, poca attemps creation of the subdirectory. Failure at this stage
causes poca to skip the subscription. The title must be a legal directory name 
on the filesystem used (linux filesystems have almost no restrictions, NTFS 
and FAT have a few).

url
^^^

The address of the RSS feed of the podcast.

That's all. If the number of optional settings are a bit overwhelming, you 
can simply leave it at that. ``max_number`` would probably be the only truly 
important non-required setting (see just below).

Optional elements
-----------------

Note that all optional elements in a subscription can also be added to the 
``<defaults>`` section to be applied globally.

max_number
^^^^^^^^^^

The maximum number of episodes (integer) for the subscription to have at any 
one time. Only the ``max_number`` most recent episodes will be downloaded. If 
this is not set poca will - unless otherwise restricted - download all files 
in the feed. This setting replaces the ``max_mb`` setting in versions of poca 
prior to 0.6.

from_the_top
^^^^^^^^^^^^

This is an alternative to default mode. The latter prioritises later episodes 
over newer: If ``max_number`` is 4, poca will download the latest 4 episodes. 
If from_the_top is set to 'yes', poca will instead start at the beginning, 
downloading the oldest 4 episodes. To move forward in the feed, you simply 
delete old files (episodes 1 and 2). Poca will detect this and fill up the 
``max_number`` quota with newer files (episodes 5 and 6). This is useful for 
audiobook-style podcasts like *Serial* or working your way through old 
episodes of a newly discovered podcast. 

track_numbering
^^^^^^^^^^^^^^^

Track numbers in podcasts are hit or miss. Some include them, some don't. 
Most players will then simply play the files in the order of filenames. If 
you want to ensure that the episodes have track numbers set to ``yes`` which 
will overwrite the episodes track number with an artificial track number that 
starts at 1 with the first episode poca downloads (so if you start 
subscribing at episode 247, this will get tracknumber 1 etc.) Set to 
``if missing`` to only insert track numbers when they are absent. 

This can be a useful setting in ``<defaults>``. Set to ``no`` or leave the 
option out of your subscription to leave the track number as is.

Note that track numbers can also be overwritten using the ``tracknumber``
element in metadata (see below). That, however only sets track numbers to a
static value - or if no value is entered removes the track numbers entirely.

metadata
^^^^^^^^

With 1.1 tagging now works for m4a files as well as vorbis comments (ogg, 
opus, flac amongst others) and id3 tags.

Each element under **metadata** is a field in the id3/m4a/vorbis comment 
header that should be overwritten or added (if there is no such field in the 
original metadata). If you do not wish to touch the vorbis comment/id3 
headers simply leave out the **metadata** element altogether. 


* Example: The 'Savage Love' podcast has the publisher 'The Stranger' as the 
  value of the 'artist' field. Creating an ``<artist>Dan Savage</artist>`` 
  element tags the downloaded files with *Dan Savage* instead.
* Example: If your player arranges files by genre, it might be advantageous 
  to have all podcasts genre labelled 'podcasts' in a uniform fashion by 
  inserting a ``<genre>podcast</genre>`` element either in each individual 
  subscription or in the ``defaults``. 

A list of all the field names that poca recognises for id3 and m4a headers can
be printed by running ``poca-subscribe tags`` using either the ``--mp3`` or
the ``--mp4`` flag.

Relying on mutagen's "easy" modules, poca allows you to use ``title`` for 
track title, ``artist`` for artist, etc. Vorbis comment tags are not restricted 
in what keys can be used (though all vorbis comment keys must be ascii) but this 
`Xiph.org list <https://xiph.org/vorbis/doc/v-comment.html>`_ can be used as a 
reference for tag names convention.

Any empty value, i.e.::

    <album></album>

or::

    <album/>

will cause the frame to be removed rather than overwritten. This especially
true for the ``<chapters/>`` element, as that can only be used to remove. poca will
disregard any text value associated with it and will only use it to remove CTOC
and CHAP frames from id3 tags in the subscription.

rename
^^^^^^

An option to rename the media files downloaded. Not all feeds name their 
media consistently, helpfully (e.g. all files are named media.mp3) or 
alphabetically (e.g. just using the episode title rather than conventions 
like padded-tracknumber_title). 

Renaming is done by slotting in the new name components as XML elements in 
the file name order desired. The available components from the feed and the 
user settings are as follows.


* ``title``\ : The title of the subscription as indicated by the user
* ``episode_title``\ : The title of the episode as indicated by the publisher 
  in the feed
* ``date``\ : The date at which the episode was published to the feed (aka 
  pubdate). The date is rendered in the format YYYY-MM-DD.
* ``uid``\ : The episode's unique identifier in the feed. This can be a 
  number (\ ``7932``\ ), a random string (\ ``d39gs9db3f6ihhbzx5``\ ) or the 
  url for the episode. All non-alphanumerical characters are discarded for 
  naming purposes.
* ``org_name``\ : The original filename for the episode. In case you just 
  want to preface it with a date or uid.

Each component can be used as many times as desired or not at all. The 
components can come in any order desired.

Please note, that the rename pattern is resolved before the file is 
downloaded. Therefore there is no option to make use of media metadata 
(id3/vorbis comments) when renaming.  Any non-available components (e.g. a 
feed does not have uids for entries) will be replaced with 'missing' or 
similar. 

By default the components are divided by underscores when assembling the full 
file name. Alternatively you can set the ``divider`` attribute and give it 
the desired divider value. Spaces in the filename originating from using a 
title or similar can be replaced by using the ``space`` attribute. Spaces 
will be replaced with the value of the attribute. Note that the resulting 
filenames are sanitized, see the *filenames* section in **Settings**.

Example:

.. code-block:: xml

   <rename divider="_" space="_">
       <date/>
       <org_name/>
   </rename>

The above configuration as applied to the Python Bytes feed result in files 
named like this:

.. code-block:: none

   2017-10-25_your-technical-skills-are-obsolete-now-what.mp3 
   2017-11-02_bundling-shipping-and-protecting-python-applications.mp3

filters
^^^^^^^

The filters element should contains one or more of the following tags that 
filter the entries in the feed based on various criteria. All filters are 
positive in the sense that the entry must meet the criterion to be included. 
Each filter can only be used once per subscription.


filename
~~~~~~~~

The filename of the entry must match this string in order to be included. 
Note that the value is interpreted as a regex, so certain characters should 
be escaped (e.g. a literal point should be written '\.') Apart from this it 
is perfectly possible to use simple strings and ignore the regex aspect. The 
filename matched is the original filename, not those resulting from using 
``rename`` (see above). Example: 

``<filename>^episode</filename>`` will only include regular Judge John Hodgman
episodes and not the special cheese shows, *shootin' the bries* that have
filenames starting with "shootin'".


title
~~~~~

The same as above, only for the title in the RSS feed (not in the music 
file's metadata). Example: 

``<title>Wires</title>`` only gets the 'Within the Wires' episodes from the 
Welcome to Nightvale feed.


hour
~~~~

The hour (24h-format) at which the entry was published. This is useful for 
podcasts that put out more episodes a day than you need, e.g. news broadcasts. Example:

``<hour>21</hour>`` only gives you the evening edition of BBC's Newshour.


weekdays
~~~~~~~~

Excludes all episodes not published on the specified weekdays. Each weekday 
to be included is written as a single digit where Monday is 0, Tuesday is 1, 
etc, up to 6 for Sunday. Example

``<weekdays>024</weekdays>`` to get Monday, Wednesday, and Friday episodes.


after_date
~~~~~~~~~~

Only includes episodes published on or at a later time than the specified 
date. Format is YYYY-MM-DD. This is useful is you don't want to restrict the 
``max_number`` of the subscription but still avoid downloading the entire 
back catalogue. Example:

``<after_date>2016-08-23</after_date>`` will ignore all episodes published 
before August 23rd 2016.


Optional attributes
-------------------

Each subscription tag can have two optional attributes:


category
^^^^^^^^^^^^^^^

Setting a category will sort the outputted list of poca-subscribe's ``list`` 
command into groups, each category being grouped together. Example: 

``<subscription category="news">...</subscription>``

.. _state:

state
^^^^^^^^^^^^^^^

The state attribute has two valid settings: ``active`` and ``inactive``. If a 
subscription does not have the attribute it is counted as being active. 
Active subscriptions are updated as normal. Inactive subscriptions are passed 
over when poca is run. Additionally, setting a subscription's state to 
inactive using poca-subscribe's ``toggle`` command will delete old audio 
files. Example:

``<subscription state="inactive">...</subscription>``


Example
-------

Here is an example of a subscription to a news in French podcast:

.. code-block:: xml

   <subscription category="news">
       <title>francais facile</title>
       <url>http://www.rfi.fr/radiofr/podcast/journalFrancaisFacile.xml</url>
       <max_number>3</max_number>
       <metadata>
           <artist>Radio France Internationale</artist>
           <album>Journal en français facile</album>
           <genre>podcast</genre>
       </metadata>
       <rename>
           <title/>
           <date/>
       </rename>
   </subscription>

