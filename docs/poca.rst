poca
====

Help
----

.. code-block:: none

    usage: poca [-h] [-q | -v] [-l] [-e] [-c CONFIG] [-g GLYPHS] [-t THREADS]

    Poca 1.1 : A fast and highly customizable command line podcast client

    optional arguments:
      -h, --help            show this help message and exit
      -q, --quiet           No output to stdout (useful for cron jobs)
      -v, --verbose         Output details on files being added and removed.
      -l, --logfile         Output to file in poca config directory
      -e, --email           Output to email (set in config)
      -c CONFIG, --config CONFIG
                            Use alternate config directory
      -g GLYPHS, --glyphs GLYPHS
                            Glyph set to use. Options: default, ascii, wsl, and
                            emoji
      -t THREADS, --threads THREADS
                            Number of concurrent downloads to allow. '--verbose'
                            forces single thread.

Output
------

In normal and verbose mode poca summarizes operations for each subscription. 
The glyphs should be interpreted as follows:

.. |userdel| unicode:: \u2718
.. |planrem| unicode:: \u2796
.. |planadd| unicode:: \u2795

- |userdel| signifies the number of user-deleted files detected
- |planrem| signifies the number of files to be removed due to to hitting the 
  ``max_number`` cap
- |planadd| signifies the number of files to be downloaded

In verbose mode poca will also generate output for each individual operation. 
The glyphs should be interpreted as follows:

.. |autodel| unicode:: \u2717
.. |download| unicode:: \u21af
.. |error| unicode:: \u203c

- |autodel| indicates deletion of a file
- |download| indicates download of a file
- |error| indicates an error

Using the -g parameter these can be changed to other glyph sets, including
WSL-friendly and ASCII-only.
