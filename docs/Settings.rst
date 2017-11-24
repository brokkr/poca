.. role:: strike
    :class: strike

Settings
========

In poca settings are general, non-podcast specific options. For all podcast specific options, see Subscriptions.

.. contents::

Structure
---------

The ``<settings>`` element contains the following required settings:


* ``basedir``

and the following optional settings:


* ``id3v2version``
* ``id3removev1``
* ``id3encoding`` (deprecated in 0.9)
* ``useragent``
* ``audiosearch`` (deprecated in 1.0)
* ``email``

Required settings
-----------------

base_dir
^^^^^^^^

The directory that will contain the audio files. Under this directory poca will create a subdirectory for each subscription:

.. code-block:: none

       base_dir
           |--- my_podcast
           |        |--- ep01.mp3
           |        |--- ep02.mp3
           |        |--- ...
           |--- my_other_podcast
           |         |--- ...
       etc.

Optional settings (id3)
-----------------------

Poca allows for modifying the metadata of the downloaded files by setting `override values <https://github.com/brokkr/poca/wiki/Subscriptions#metadata>`_. Within the 'settings' context two options allow you to choose what format poca should use when writing id3 headers. There are no settings needed for writing vorbis comments in ogg, flac, etc.

id3v2version
^^^^^^^^^^^^

``id3v2version`` accepts ``3`` or ``4`` as settings, representing id3v2.3 and id3v2.4 respectively.Historically, Windows and some hardware players have preferred v2.3 as they cannot read the UTF-8 characters used in v2.4. Default is ``4``.

id3removev1
^^^^^^^^^^^

This allows you to remove id3v1 headers (if any exist) from the files. It has the valid values **yes** and **no**. It will only be applied in any given subscription if the subscription settings (or defaults) include id3 overrides.

id3encoding (deprecated in 0.9)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

id3encoding didn't really do what it said on the tin because each frame (artist, album, title, etc.) in an id3 header is separately encoded and the encoding would only apply to new or overwritten frames. As the real distinction is between players that prefer v2.3 (using a mixture of latin1 and utf16 frames) and v2.4 (using a mixture of latin1 and utf8 frames), the setting has been depecated since 0.9

Optional settings (other)
-------------------------

useragent
^^^^^^^^^

This is a fallback option. Poca will always first attempt download with the 'honest' user agent declaration (Python's *request* library). Setting ``useragent`` allows poca to make a second attempt in case of failure due to blocking, only this time with a spoofed user agent. Enter any user agent string you want - you can find some useful ones in `this big list <https://techblog.willshouse.com/2012/01/03/most-common-user-agents/>`_ - or leave it empty/remove it if you don't want poca to use spoofing. We suggest you leave as it is and only return to it if you see lots of messages like this when you run poca: "Download failed. HTTP Error 403: Forbidden".

audiosearch (deprecated in 1.0)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As of November 28 2017 audiosear.ch will cease operations. Therefore the ``poca-subscribe search`` functionality has been removed from the 1.0 release.

Application oauth id and secret required for using the Audiosear.ch API with ``poca-subscribe search``. For more on the functionality see the wiki on `poca-subscribe search <https://github.com/brokkr/poca/wiki/poca-subscribe#search>`_. To register your application and get your own id/secret, please go to `https://www.audiosear.ch/oauth/applications <https://www.audiosear.ch/oauth/applications>`_.

Example:

.. code-block:: xml

   <audiosearch>
       <id>t7h9as6fnojimcyr53eqcrykpcrnbjb77en70sqtsqbamelh54q6enkil1u8edvb</id>
       <secret>6uh70n1noucy201qaddgwhmwnhmc9cuilgcix9n4wg7pk3smmqjdcmrjuhbhfbvs</secret>
   </audiosearch>

email
^^^^^

In order to properly enable email logging (\ ``poca -e``\ ) you will need a working email setup in your settings section. To keep things simple the email tag and its sub-tags will not appear in a standard auto-generated ``poca.xml`` file. You will need to add them manually.

Email logging works similar to file logging in that poca summarizes changes to a subscription rather than listing each new/deleted episode individually. At the end of a run Poca will send off one email (if there have been sufficient changes) or none if not much has changed. See ``threshold`` below for details.

The following settings are used:


* **only_errors**\ : If set to ``yes``\ , only errors will be logged to email. This does not affect file logging. If set to ``no`` all the notifications you find in the file log will go into the log emails as well (episodes downloaded, removed, user deleted etc.). *Default is ``no``.*
* **threshold**\ : The number of entries required before an email is sent. At the end of the run the number of logged entries is compared to the ``threshold`` value and if it is equal to or greater than that number, the logged entries are emailed off and the cache is cleared. Otherwise the entries are saved to the cache and included next time Poca runs. So a value of 1 means that a run that produces any entries (or errors if only_errors is set) will fire off an email. A run that produces 56 entries will likewise fire off a single email. A run that produces no entries will not result in an email. Increasing this setting is mostly useful in combination with **only_errors**. By setting a threshold of say 20 or 30, you will get notified when your subscriptions consistently produce errors (e.g. a feed is not working anymore) but not (instantly) when a server is merely offline for an hour or a single request gets lost. *Default is ``1``.*
* **fromaddr**\ : The sender address for the log emails. *No default*
* **toaddr**\ : The recipient address for the log emails. *No default*
* **host**\ : The email server's name/address. *Default is ``localhost``.*
* **starttls**\ : To keep things simple Poca only accepts two kinds of setup: Either you relay without authentication on port 25 (probably only local servers) or you do submission with STARTTLS on port 587. Enter ``yes`` for the latter, ``no`` for the former. Choosing ``yes`` will require a ``<password>`` entry (see below), choosing ``no`` will not. Default is ``no``.
* **password**\ : The password for the SMTP server. Only used with STARTTLS set to ``yes``.

If you intend to use a Gmail account for this purpose, please be aware that you'll need to allow access for `insecure apps <https://support.google.com/accounts/answer/6010255>`_ in order for password authentication over STARTTLS to work. 

Examples
~~~~~~~~

.. code-block:: xml

       <email>
           <fromaddr>me@localhost</fromaddr>
           <toaddr>me@localhost</toaddr>
       </email>

The very minimal configuration sends off one email for each run that produces any output. It relies on a local smtp server that accepts emails originating from the machine itself unquestioningly.

.. code-block:: xml

       <email>
           <only_errors>yes</only_errors>
           <threshold>20</threshold>
           <host>smtp.gmail.com</host>
           <starttls>yes</starttls>
           <password>123456</password>
           <fromaddr>mypocainstance@gmail.com</fromaddr>
           <toaddr>me@hotmail.com</toaddr>
       </email>

The full STARTTLS setup overriding defaults. It will only inform us of errors and when at least 20 have been logged, either in a single run or over multiple runs. It will authenticate over STARTTLS (the standard login/password way of authenticating when using any email client) and send your password over an encrypted channel to gmail.com. Do note that even though the password is only transmitted over encrypted channels, it is plaintext on your machine, so think about what account you use for this purpose.
