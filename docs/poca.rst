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
