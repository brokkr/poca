## Poca
Poca is a command line podcast client, written in Python 3. It is developed for
stability and ease of use.

### Features
With Poca you can set custom options for each individual subscription. 

 * **Maximum amount**. Specify how many episodes the subscription should get 
   before deleting old episodes to make room for new ones.
 * **Override ID3/Vorbis metadata**. If you want 'Savage Love' to have Dan 
   Savage in the artist field (rather than The Stranger), poca will 
   automatically update the metadata upon download of each new episode. Set
   'genre' to be overwritten by 'Podcast' as a default. Or have poca add track
   numbers to shows that have forgotten them.
 * **Filter a feed** using criteria such as filename and title, or the hour,
   weekday or date of publishing. Only want news reports in the morning or on
   Wednesdays? You got it.
 * **From the top**. Some podcasts are best if you start at the beginning. Poca 
   introduces a special mode that gets the oldest episodes first, rather 
   than the latest. To move on to later episodes simply delete old ones and 
   poca will fill up with the next in line.
 * **Keeping track**. Poca logs downloads and removals to a local file so you
   easily see what's changed. Or configure it with an SMTP server and get
   notified when a feed stops working.
 * **Manage your shows** by editing an easy-to-understand xml file. Or use
   the accompanying tool to add, delete, sort them and get neat (!) ascii
   graphs showing the publishing frequency, average episode length and more.
 * **... and find new ones** with the accompanying search tool using the
   Audiosear.ch API.

Poca also: has excellent unicode support for feeds, filenames and tags, gets 
cover images for feeds, has the ability to spoof user agents, can pause your
subscriptions, remembers which downloads actually completed, and more.

See the [Configuration](https://github.com/brokkr/poca/wiki/Configuration) section of the
wiki for more details on features.

### Interface
[![asciicast](https://asciinema.org/a/cwf8k4e154s6dkw2hiohqxj68.png)](https://asciinema.org/a/cwf8k4e154s6dkw2hiohqxj68)

Poca is designed to be as intutive as possible. All configuration is done in 
a single XML-format file and the output is easy to read. For maximal cron job 
compatibility, Poca has both a file logging and quiet mode.

### Installing
You can install poca using only setuptools but `pip` is recommended. Find pip 
for your distro in your repositories (for debian/ubuntu its "python3-pip")

To generate a package installable by pip, in the source root directory (the 
one with setup.py) do:

    python3 ./setup.py sdist

And then install the generated package (using root privileges)

    pip3 install ./dist/poca-[VERSION].tar.gz

Running `poca` on a fresh install (no configuration) will place a copy of the 
example configuration in ~/.poca. The included feeds are there for illustrative
purposes. Edit the configuration file, try them out or use `poca-subscribe
delete` to clear it out and start afresh.

To remove Poca - having installed it using pip - simply do:

    pip3 uninstall poca

### Dependencies
 * You will need Python 3 for setup and running the program
 * The following third-party modules are required: `feedparser`, `lxml`, `mutagen`
 * The following third-party modules are recommended: `audiosearch`
 * Pip can install all of these using 'pip3 install [name of module]'
