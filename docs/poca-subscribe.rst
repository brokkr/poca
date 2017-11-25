poca-subscribe
==============

Help
----

.. code-block:: none

   usage: poca-subscribe [-h] [-c CONFIG]
                         {add,list,tags,delete,toggle,stats} ...

   poca-subscribe 1.0 : A subscription management tool for poca

   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           Use alternate config directory

   commands:
     'poca-subscribe command --help' for futher information

     {add,list,tags,delete,toggle,stats}
       add                 Add a new subscription interactively
       list                List current subscriptions
       tags                List available id3 tags
       delete              Remove subscription, delete files
       toggle              Set state of current subscriptions
       stats               Get feed stats for current subscriptions

Each command also has it's own set of flags/arguments. Run ``poca-subscribe 
[command] --help`` to see them. 

Commands
--------

add
^^^

Add a subscription. ``add`` starts up a step-by-step setup assistant that 
allows you to enter a title, url, max_number setting etc. Once completed, 
the resulting subscription is added to your poca.xml. Does not at the moment 
allow for metadata and filters settings to be added.

This is an easy-to-use way to quickly add some subscriptions if you're not 
entirely comfortable editing xml.

stats
^^^^^

Get some basic stats on a current subscription. Use -t [title] for matching 
against the subscription title, -u [url] for matching against the url (e.g. 
check all subs from the BBC). If no matching is done it will loop through all 
current subs. Prints:


* publishing frequency over the past five weeks (how many episodes and on 
  what weekdays they publish)
* latest episode title and date
* average size (Mb) and length (hours:minutes) of an episode

``stats`` is automatically called when using ``add`` after entering a url.

Example:

.. code-block:: none

   PYTHON BYTES
   Author: Michael Kennedy                                  PUBLISHED / 5 WEEKS
   Title:  Python Bytes

   Last episode: #29 Responsive Bar Charts with Bokeh
   Published:    08 Jun 2017                                             ▮
                                                                      ▮  ▮
   Avg. size of episode:   15 Mb                                      ▮  ▮
   Avg. length of episode: 20m                               M  T  W  T  F  S  S

delete
^^^^^^

Delete a subscription. Goes through all subscriptions and asks you to decide 
on delete/keep. List can be narrowed using the command-specific ``-t/--title 
TITLE`` or ``-u/--url URL`` parameters.

toggle
^^^^^^

Toggle the :ref:`state` attribute of a subscription between active and 
inactive. Goes through all subscriptions and asks you to decide on setting as 
active or inactive. Inactive subscriptions are not updated. Subscriptions 
with no state attribute are considered active. List can be narrowed using the 
command-specific ``-t/--title TITLE`` or ``-u/--url URL`` parameters.

list
^^^^

Prints out a list of subscriptions. List is sorted by category attribute if 
any are present.

tags
^^^^

Prints out all useable id3 tags (use grep/less). Poca uses Mutagen's 
`EasyID3 <http://mutagen.readthedocs.io/en/latest/user/id3.html#easy-id3>`_ 
editor so it understands sensible tag names, i.e. 

Don't:

.. code-block:: xml

   <metadata>
       <TALB>Call of the Wild<TALB>
   </metadata>

Do:

.. code-block:: xml

   <metadata>
       <album>Call of the Wild<album>
   </metadata>

Ogg, FLAC et al. use VorbisComment with no restrictions on tag names (though 
there are `conventions <https://xiph.org/vorbis/doc/v-comment.html>`_).
