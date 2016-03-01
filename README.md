##Poca
Poca is a command line podcast client, written in Python. 

Functionality-wise, the focus is - as the name hints at - to reign in its 
appetite: Subscribing to a feed should not mean downloading each new episode 
until the harddrive is groaning under the weight, rather it should mean having 
the latest episodes available while old ones are discarded. This is done by 
specifying the amount of disk space allocated to each feed.
 
As for user interface and design, Poca is intended to be a powerful and 
easy-to-use podcast tool (also in the \*NIX spirit) rather than pre-molded 
podcast package. This leaves extensive options in the hands of the user, 
including id3 tagging, cronjob compatibility, error logging prefs, etc.

####Future plans
 * 0.3.1: Nicer output, colors
 * 0.3.2: Debug output option, awareness of info-error-critical levels
 * 0.3.3: Reimplement file logger
 * 0.4:  ID3 tagging reimplemented using mutagen. Includes id3 version and
   encoding preferences and extensive frame override support. Improved output.
 * 0.5:  Renaming files from tags and/or podcast metadata.
 * 0.6:  Self-righting: Insuring that the db and the files on disk never get
   out of sync whatever happens.
 * 0.7:  Maximum can be specified as space and/or number of episodes or left
   out entirely.
 * 0.8:  Support for .ogg and other formats
 * 0.9:  Subscription editing via the command line. Default suggestions (i.e.
   title) are presented to user. Possible [search engine addition]
   (http://stackoverflow.com/questions/3201052/podcast-search-api).

###Installing
To install to /usr/local simply do

    sudo python2 ./setup.py install

setup.py is geared for install on POSIX environments. This means that the 
following assumptions are made as regards file placement:
 * An example configuration file ('poca.xml') is put in the '/etc' directory. 
   The file contains commented examples of subscriptions that should make it 
   easy to add your own.
 * Running 'poca' on a fresh install (no configuration) will place a copy of
   the example configuration in ~/.poca.
 * The man page is put in 'share/man/man1', inside of the installation prefix
   (usually '/usr' or '/usr/local')
If this is unacceptable, please patch the setup.py file or contact the author.

###Dependencies
* You will need to use Python2 (not Python3) for both setup and running the program.
* In order for XML parsing to work (elementTree), Python 2.5 or higher is required.
* The following third-party modules are required: feedparser, mutagen.
* Pip can install all of these using 'pip install [name of module]'

