.. role:: strike
    :class: strike

Settings
========

In poca settings are general, non-podcast specific options. For all podcast 
specific options, see :doc:`Subscriptions`.

.. contents::

XML
---

When entering text values into poca.xml settings elements, as in

.. code-block:: xml

       <setting>text_value</setting>

you can use any unicode character directly without resorting to escapes or code
point values. I.e. this is valid:

.. code-block:: xml

       <setting>🎞️ and 🍿</setting>

The only exceptions to this rule are

* ``<`` or less than - to insert, use the code ``&lt;``
* ``&`` or ampersand - to insert, use the code ``&amp;``

E.g. to enter the value *me & my*, use

.. code-block:: xml

       <setting>🎞️ &amp; 🍿</setting>


Structure
---------

The ``<settings>`` element contains the following required settings:


* ``basedir``

and the following optional settings:


* ``id3v2version``
* ``id3removev1``
* ``filenames``
* ``useragent``
* ``email``

Required settings
-----------------

base_dir
^^^^^^^^

The directory that will contain the audio files. Under this directory poca 
will create a subdirectory for each subscription:

.. code-block:: none

       base_dir
           |--- my_podcast
           |        |--- ep01.mp3
           |        |--- ep02.mp3
           |        |--- ...
           |--- my_other_podcast
           |         |--- ...
       etc.

At startup poca tests if ``base_dir`` exists and the user has write permissions
to it. If it does not, poca tries to create it. Failure at this stage causes
poca to quit with a failure message. Remember that base_dir must be a legal
path on the filesystem used.

Optional settings (id3)
-----------------------

Poca allows for modifying the metadata of the downloaded files by setting 
`override values <https://github.com/brokkr/poca/wiki/Subscriptions#metadata>`_. 
Within the 'settings' context two options allow you to choose what format 
poca should use when writing id3 headers. There are no settings needed for 
writing vorbis comments in ogg, flac, etc.

id3v2version
^^^^^^^^^^^^

``id3v2version`` accepts ``3`` or ``4`` as settings, representing id3v2.3 
and id3v2.4 respectively. Historically, Windows and some hardware players 
have preferred v2.3 as they cannot read the UTF-8 encoded characters used 
in v2.4. Default is ``4``.

id3removev1
^^^^^^^^^^^

This allows you to remove id3v1 headers (if any exist) from the files. It 
has the valid values **yes** and **no**. It will only be applied in any given 
subscription if the subscription settings (or defaults) include id3 overrides.

Optional settings (other)
-------------------------

useragent
^^^^^^^^^

This is a fallback option. Poca will always first attempt download with the 
'honest' user agent declaration (Python's *request* library). Setting 
``useragent`` allows poca to make a second attempt in case of failure due to 
blocking, only this time with a spoofed user agent. Enter any user agent 
string you want - you can find some useful ones in `this big list 
<https://techblog.willshouse.com/2012/01/03/most-common-user-agents/>`_ - or 
leave it empty/remove it if you don't want poca to use spoofing. We suggest 
you leave as it is and only return to it if you see lots of messages like 
this when you run poca: "Download failed. HTTP Error 403: Forbidden".

filenames (new in 1.1)
^^^^^^^^^^^^^^^^^^^^^^

The filenames setting allows the user to set an upper level of filename
character permissiveness. Some filesystems allow for more characters in 
filenames than others. Poca handles this by trying four different filenaming
restriction settings, one after the other, in order of decreasing
'permissiveness'. In other words: The more attempts, the more characters are
removed from the filename of the file being written. This system mostly comes
into effect when using feed data to generate a filename using the rename
scheme. The four levels are:

* ``permissive``: Only ``/`` and ␀ (the null character) are removed from
  the filename. These are the only characters that are outright forbidden on
  linux file systems, like ext4 and others.
* ``ntfs``: Any characters that are not acceptable on NTFS and FAT filesystems
  (mounted using VFAT, the restrictions are the same for FAT as for NTFS) are 
  removed from the filename. That includes all control characters, slashes
  (backward and forward), colons, asterisks, question marks etc.
* ``restrictive``: Unlike permissive and ntfs, restrictive is defined by the
  characters included, not by those removed. Accepted characters are
  alphanumerical, hyphens, and underscores. In regex terms: [a-zA-Z0-9_\-].
  Spaces are converted to underscores, rather than removed.
* ``fallback``: This option is defined as the publishing date of the entry in 
  the feed in the format YYYY-MM-DD, followed by 9 random hexadecimal digits.

``permissive`` and ``ntfs`` both retain all (non-excluded) unicode characters. 
The filenames setting does not definitively determine the scheme, poca will 
use. It allows the user to set a 'lower' starting point than would otherwise 
be used. The default starting point is the ``permissive`` setting.

Ordinarily, poca will attempt the schemes in the order listed. Filesystem
failures will cause it to move on to the next scheme. If the files are to be
shared using a protocol, less tolerant of filename characters than the
filesystem used, it might be preferable to have poca apply more restrictions
from the start rather than having to rename them later. E.g. ext4 filesystem
but the files are made accessible via SAMBA/CIFS.

The setting applies regardless of whether a subscription uses the default, 
original filenames or a rename scheme. It is applied only to the basename, 
and after a possible ``rename`` operation.

Note that the ``fallback`` setting will also be applied regardless of user
settings, if poca detects that multiple entries to be downloaded will have the
same filename if the configuration is followed to the letter. E.g. if no rename
scheme is in effect with a subscription from acast.com (which names every file
media.mp3) or if the user has chosen [subscription title].mp3 as the rename
scheme.

email
^^^^^

In order to properly enable email logging (\ ``poca -e``\ ) you will need a 
working email setup in your settings section. To keep things simple the email 
tag and its sub-tags will not appear in a standard auto-generated ``poca.xml`` 
file. You will need to add them manually.

Email logging works similar to file logging in that poca summarizes changes 
to a subscription rather than listing each new/deleted episode individually. 
At the end of a run Poca will send off one email (if there have been 
sufficient changes) or none if not much has changed. See ``threshold`` below 
for details.

The following settings are used:


* **only_errors**\ : If set to ``yes``\ , only errors will be logged to 
  email. This does not affect file logging. If set to ``no`` all the 
  notifications you find in the file log will go into the log emails as well 
  (episodes downloaded, removed, user deleted etc.). *Default is ``no``.*
* **threshold**\ : The number of entries required before an email is sent. At 
  the end of the run the number of logged entries is compared to the 
  ``threshold`` value and if it is equal to or greater than that number, the 
  logged entries are emailed off and the cache is cleared. Otherwise the 
  entries are saved to the cache and included next time Poca runs. So a value 
  of 1 means that a run that produces any entries (or errors if only_errors 
  is set) will fire off an email. A run that produces 56 entries will 
  likewise fire off a single email. A run that produces no entries will not 
  result in an email. Increasing this setting is mostly useful in combination 
  with **only_errors**. By setting a threshold of say 20 or 30, you will get 
  notified when your subscriptions consistently produce errors (e.g. a feed 
  is not working anymore) but not (instantly) when a server is merely offline 
  for an hour or a single request gets lost. *Default is ``1``.*
* **fromaddr**\ : The sender address for the log emails. *No default*
* **toaddr**\ : The recipient address for the log emails. *No default*
* **host**\ : The email server's name/address. *Default is ``localhost``.*
* **starttls**\ : To keep things simple Poca only accepts two kinds of setup: 
  Either you relay without authentication on port 25 (probably only local 
  servers) or you do submission with STARTTLS on port 587. Enter ``yes`` for 
  the latter, ``no`` for the former. Choosing ``yes`` will require a 
  ``<password>`` entry (see below), choosing ``no`` will not. Default is 
  ``no``.
* **password**\ : The password for the SMTP server. Only used with STARTTLS 
  set to ``yes``.

If you intend to use a Gmail account for this purpose, please be aware that 
you'll need to allow access for 
`insecure apps <https://support.google.com/accounts/answer/6010255>`_ in 
order for password authentication over STARTTLS to work. 

Examples
~~~~~~~~

.. code-block:: xml

       <email>
           <fromaddr>me@localhost</fromaddr>
           <toaddr>me@localhost</toaddr>
       </email>

The very minimal configuration sends off one email for each run that produces 
any output. It relies on a local smtp server that accepts emails originating 
from the machine itself unquestioningly.

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

The full STARTTLS setup overriding defaults. It will only inform us of errors 
and when at least 20 have been logged, either in a single run or over 
multiple runs. It will authenticate over STARTTLS (the standard 
login/password way of authenticating when using any email client) and send 
your password over an encrypted channel to gmail.com. Do note that even 
though the password is only transmitted over encrypted channels, it is 
plaintext on your machine, so think about what account you use for this 
purpose.
