##Poca 1.1.2 Update
Poca has been moved from Google Code to Github and brought into 2015, having
lingered in 2011 for some years. This means that 
* ~~id3 tagging has been disabled (for now) due to issues with more recent eyed3 
  versions.~~ Reinserted using mutagen.
* ~~'Urlgrabber' module has been replaced by 'requests'. This means more troublefree 
  downloads. It also means no more progressmeter. It also also means that quiet /
  cron mode is no longer guaranteed to be silent (for now).~~ No external
  dependencies for file downloads (using urllib2 for silent and progress
  downloads)
* The switch to sqlite logging in the more 'recent' code has been reversed as has
  a half-hearted attempt to go multiprocess.

Other than that things should work. 

####Future plans
 * 0.2: ID3 tagging reimplemented using mutagen. Includes id3 version and
   encoding preferences and extensive frame override support. Quiet and
   progress download modes supported.
 * 0.3: Code cleanup. Feedparser dependency eliminated (possibly).
 * 0.4: Sqlite (or other db) logging reimplemented.

##Poca
Poca is a command line podcast client, written in Python. Though started as a 
simple learning project script, it has grown to be a solid, capable program, 
that in the best \*NIX tradition attemps to "do one thing and do it well".

Functionality-wise, the focus is - as the name hints at - to reign in its 
appetite: Subscribing to a feed should not simply downloading each new episode 
until the harddrive is groaning under the weight, rather it should mean having 
the latest episodes available while old ones are deleted. This is done by 
specifying the amount of disk space allocated to each feed.
 
As for user interface and design, Poca is intended to be a powerful and 
easy-to-use podcast tool (also in the \*NIX spirit) rather than pre-molded 
podcast package. This leaves extensive options in the hands of the user, 
including id3 tagging, cronjob compatibility, error logging prefs, etc.

###Installing
To install to /usr/local simply do

    sudo python2 ./setup.py install

setup.py is geared for install on POSIX environments. This means that the 
following assumptions are made as regards file placement:
 * An example configuration file 8'poca.xml') is put in the '/etc' directory. 
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

