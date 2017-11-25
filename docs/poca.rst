poca
====

Help
----

.. code-block:: none

    usage: poca [-h] [-q | -v] [-l] [-e] [-c CONFIG] [-t THREADS]

    Poca 1.0 : A fast and highly customizable command line podcast client

    optional arguments:
      -h, --help            show this help message and exit
      -q, --quiet           No output to stdout (useful for cron jobs)
      -v, --verbose         Output details on files being added and removed.
      -l, --logfile         Output to file in poca config directory
      -e, --email           Output to email (set in config)
      -c CONFIG, --config CONFIG
                            Use alternate config directory
      -t THREADS, --threads THREADS
                            Number of concurrent downloads to allow. '--verbose'
                            forces single thread.

Output
------

In normal and verbose mode poca summarizes operations for each subscription. 
The glyphs should be interpreted as follows:

.. |circle_x| unicode:: \u29bb
.. |heavy_minus_sign| unicode:: \u2796
.. |heavy_plus_sign| unicode:: \u2795

- |circle_x| signifies the number of user-deleted files detected
- |heavy_minus_sign| signifies the number of automatically deleted files due
  to hitting the ``max_number`` cap
- |heavy_plus_sign| signifies the number of files to be downloaded

In verbose mode poca will also generate output for each individual operation. 
The glyphs should be interpreted as follows:

.. |cross_mark| unicode:: \u274c
.. |up_down_arrow| unicode:: \u21f5
.. |warning_sign| unicode:: \u26a0

- |cross_mark| indicates deletion of a file
- |up_down_arrow| indicates download of a file
- |warning_sign| indicates an error
