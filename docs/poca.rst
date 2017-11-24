
Help
----

.. code-block:: none

   usage: poca [-h] [-q | -v] [-l] [-e] [-c CONFIG] [-t THREADS]

   Poca threads : A cron-friendly command line podcast aggregator

   optional arguments:
     -h, --help            show this help message and exit
     -q, --quiet           No output to stdout (useful for cron jobs)
     -v, --verbose         Output details on files being added and removed. Do
                           not use with multiple concurrent downloads ('-t
                           [threads]')
     -l, --logfile         Output to file in poca config directory
     -e, --email           Output to email (set in config)
     -c CONFIG, --config CONFIG
                           Use alternate config directory
     -t THREADS, --threads THREADS
                           Number of concurrent downloads to allow

Configuration
-------------

Please see `Configuration <https://github.com/brokkr/poca/wiki/Configuration>`_ for details.
