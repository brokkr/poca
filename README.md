##Poca
Poca is a command line podcast client, written in Python. Up until release 0.3
it is written in Python 2. The upcoming 0.4 release aims to port it to python
3 with no backwards compatibility.

Functionality-wise, the focus is - as the name hints at - to reign in its 
appetite: Subscribing to a feed should not mean downloading each new episode 
until the harddrive is groaning under the weight, rather it should mean having 
the latest episodes available while old ones are discarded. This is done by 
specifying the amount of disk space allocated to each feed.
 
As for user interface and design, Poca is intended to be a powerful and 
easy-to-use podcast tool rather than pre-molded podcast package. This 
leaves extensive options in the hands of the user, including id3 tagging, 
cronjob compatibility, error logging prefs, etc.

####Future plans
* 0.4: Python 3 port
* 0.4.1: Revised output handling, debug output option, awareness of info-
  error-critical levels
* 0.5: ID3 tagging reimplemented using mutagen. 

###Installing
To install to simply do

    sudo python3 ./setup.py install (on 0.4 or later)

or

    sudo python2 ./setup.py install (on 0.3 or earlier)

Running 'poca' on a fresh install (no configuration) will place a copy of the 
example configuration in ~/.poca. The man page is put in 'share/man/man1', 
inside of the installation prefix (usually '/usr' or '/usr/local'). If this 
is unacceptable, please patch the setup.py file.

###Dependencies
* You will need Python 3 for setup and running the program.
* The following third-party modules are required: feedparser, mutagen.
* Pip can install all of these using 'pip3 install [name of module]' (or pip2
  as the case may be)

