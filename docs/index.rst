.. poca documentation master file, created by
   sphinx-quickstart on Fri Nov 24 09:28:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Poca
====

Installation
------------

You can install poca from `pypi <https://pypi.python.org/pypi/poca>`_ using
pip. Be mindful that poca is python 3 so use ``pip3``\ :

.. code-block:: none

   pip3 install poca


To remove Poca - having installed it using pip - simply do:

.. code-block:: none

   pip3 uninstall poca


Configuration
-------------

The ``poca.xml`` file contains all poca's general and subscription specific configuration. To get started simply run ``poca`` once to get a basic config file placed in ``~/.poca``. 

The configuration file *must validate as correct XML*. If you get errors related to the configuration file, please use an online xml validation service (google 'xml validation' to find any number of such services) to check if your file validates before submitting error reports. There is no need for quotes or escaping characters, simply enter values between tags. This goes for titles, paths, regexes and urls.

The configuration file is created to be as self-explanatory as possible. It is divided into three main parts:

* **Settings**: Contains general settings
* **Subscriptions**: Contains a list of all the podcasts you want to subscribe to
* **Defaults**: Options in Defaults are similar to those in Subscriptions, only they apply globally, to all subscriptions (unless overridden).

.. toctree::
   :maxdepth: 2

   Settings
   Subscriptions


Running
-------

Poca is run issuing the ``poca`` command. Subscriptions can be managed by using the helper script ``poca-subscribe``.

.. toctree::
   :maxdepth: 2

   poca
   poca-subscribe

Releases
--------

.. toctree::
   :maxdepth: 2

   Release-notes
