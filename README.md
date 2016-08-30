##Poca
Poca is a command line podcast client, written in Python 3. It is developed for
stability, hardiness and ease of use.

With Poca you can set custom options for each individual subscription. 

 * Specify how much harddisk space the subscription should use before deleting
   old episodes to make room for new ones.
 * Set overrides for the ID3 metadata. If you want 'Savage Love' to have Dan 
   Savage in the artist field (rather than The Stranger), poca will 
   automatically update the metadata upon download of each new episode. Or tag
   all your podcasts with 'podcast' as genre.
 * Name the podcast yourself and determine in what folder it goes. In a later
   version Poca will allow for autmatically renaming the files using sources
   including ID3 metadata, the feed and context (e.g. date and time).

Interface-wise Poca is designed to be as intutive as possible. All
configuration is done in a single XML-format file and the output is easy to
read. For maximal cron job compatibility, Poca has both a file logging and
quiet mode.

###Installing
You can install poca using only setuptools but 'pip' is recommended. Find pip 
for your distro in your repositories (for debian/ubuntu its "python3-pip")

To generate a package installable by pip, in the source root directory (the 
one with setup.py) do:

    python3 ./setup.py sdist

And then install the generated package (using root privileges)

    pip3 install ./dist/poca-[VERSION].tar.gz

Running 'poca' on a fresh install (no configuration) will place a copy of the 
example configuration in ~/.poca. Edit it to add your feeds.

To remove Poca - having installed it using pip - simply do:

    pip3 uninstall poca

###Dependencies
 * You will need Python 3 for setup and running the program.
 * The following third-party modules are required: feedparser, mutagen.
 * Pip can install both  of these using 'pip3 install [name of module]' 

