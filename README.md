Poca
====

Poca is a fast, multithreaded and highly customizable command line podcast 
client, written in Python 3.

Features
--------

-   **Maximum amount.** Specify how many episodes the subscription should get 
before deleting old episodes to make room for new ones.
-   **Override ID3/MP4/Vorbis metadata.** If you want *Savage Love* to have 
   *Dan Savage* in the artist field (rather than *The Stranger*), poca will 
   automatically update the metadata upon download of each new episode. Or set 
   genre to be overwritten by *Podcast* as a default.
-   **Filter a feed.** Only want news reports in the morning or on 
Wednesdays? Use criteria such as filename and title, or the hour, weekday or 
date of publishing to filter what you want from a feed.
-   **Rename files automatically.** Not all feeds have sensibly named media 
files. Specify a renaming template like date\_title to know what you're 
dealing with or to get alphabetical ordering to match chronology.
-   **From the top.** A latecomer to *Serial* or other audiobook style 
podcasts? Specify `from_the_top` to get oldest episodes first, rather than 
the latest. To move on to later episodes simply delete old ones and poca will 
fill up with the next in line.
-   **Keeping track.** Poca logs downloads and removals to a local file so 
you easily see what's changed. Or configure it with an SMTP server and get 
notified when a feed stops working.
-   **Manage your shows** by editing an easy-to-understand xml file. Or use 
the accompanying tool to add, delete, sort them, or get info about their 
publishing frequency, average episode length and more.

Poca also: has excellent unicode support for feeds, filenames and tags, gets 
cover images for feeds, has the ability to spoof user agents, can pause your 
subscriptions, deals intelligently with interruptions, updates moved feeds 
(HTTP 301) automatically, and more.

Interface
---------

[![asciicast](https://asciinema.org/a/kQkIACs7YN0dB208yzBaKfcdc.svg)](https://asciinema.org/a/kQkIACs7YN0dB208yzBaKfcdc)

All configuration is done in a single XML-format file. For cron job 
compatibility, Poca has a quiet mode in addition to normal and verbose.

Installation
------------

You can install poca from [pypi](https://pypi.python.org/pypi/poca) using pip.

``` sourceCode
pip3 install poca
```

If you are upgrading from any pre-1.0 release, please see this 
[upgrade notice](https://poca.readthedocs.io/en/latest/Upgrade.html). To 
remove Poca simply do:

``` sourceCode
pip3 uninstall poca
```

### Requirements

-   Python 3.6 or later
-   Third-party modules: `requests` `feedparser` `lxml` `mutagen`
-   Pip will automatically install any one of these found missing
-   A unicode capable terminal is recommended but not required
-   Due to dependencies of third-party modules (lxml requires libxml2 v. 2.9.2 
  and libxslt 1.1.27) distros no older than Ubuntu 18.04 are recommended.
- For use on WSL, the "-g wsl" flag is recommended as it will substitute out 
  characters known not to work on WSL (see 
  https://github.com/microsoft/WSL/issues/75)

Quickstart
----------

``` sourceCode
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
```


Links
-----

-   Homepage: <https://projects.brokkr.net/projects/poca>
-   Source code: <https://github.com/brokkr/poca>
-   Python Package Index (pypi): <https://pypi.python.org/pypi/poca>
-   Documentation: <https://poca.readthedocs.io/en/latest/>

