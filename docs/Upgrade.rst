Upgrade to 1.0 notice
=====================


If you are upgrading to 1.0 from any previous release, please note that the 
1.0 database is not backwards compatible.


Data and media files
--------------------


This means you will need to delete your ``db`` folder. You should also delete
the old media files as ``poca`` will no longer be aware of them and so either
overwrite them or ignore them.

- The ``db`` folder can be found in the config directory (``~/.poca/db`` by 
  default)
- The media files are in the folder designated by the ``base_dir`` setting in 
  poca.xml (``~/poca`` by default). 

Running ``poca`` 1.0 on an old install should alert you to the need to reset
the db as well.


Configuration file
------------------


Older versions of ``poca.xml`` will work with 1.0 but be aware that new 
options have been added and others deprecated. See :doc:`Settings` for 
details.
