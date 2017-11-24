Releases
========


Version `1.0 <https://github.com/brokkr/poca/issues?q=is%3Aopen+is%3Aissue+milestone%3A1.0>`_
-----------------------------------------------------------------------------------------------------------


* Added file renaming options (\ `#18 <https://github.com/brokkr/poca/issues/16>`_\ )
* More consistent output in normal and verbose mode
* audiosearch api removed again due to service closure (\ `#87 <https://github.com/brokkr/poca/issues/87>`_\ )
* Bugfixes, quibbles and niggles aplenty

Version `0.9 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.9>`_
-----------------------------------------------------------------------------------------------------------


* 'Artificial' track numbers (\ `issue #43 <https://github.com/brokkr/poca/issues/43>`_\ )
* Support for tagging with other formats than mp3: Ogg, opus, mp4, flac, ... (\ `issue #18 <https://github.com/brokkr/poca/issues/18>`_\ )
* Reintroduced support for id3v2.3
* poca-subscribe search: Seach for shows with audiosearch's api
* 'Preview' feed in poca-subscribe's add command (\ `issue #55 <https://github.com/brokkr/poca/issues/55>`_\ )
* Multithreading support with option for concurrent downloads as well as concurrent updates (\ `issue #45 <https://github.com/brokkr/poca/issues/45>`_\ )
* Subscription URLs are automatically updated when feeds move (HTTP status code 301)
* New dependency: Using ``requests`` library for download due to downloading in threads (urllib says no)

Version `0.8 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.8>`_
-----------------------------------------------------------------------------------------------------------


* Greatly simplified configuration parsing with lxml (new dependency)
* System defaults in case of missing or bad config and user set global subscription defaults, like setting  max_number to 3 unless overridden on a sub-specific basis.
* poca-subscribe is a new cli tool to manage subscriptions

Version `0.7 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.7>`_
-----------------------------------------------------------------------------------------------------------


* Log: Terse logging (skip writing about subscription if nothing has changed) (\ `issue #32 <https://github.com/brokkr/poca/issues/32>`_\ )
* Email logging: A sensible email logging system (\ `issue #26 <https://github.com/brokkr/poca/issues/26>`_\ )
* Style: Investigating Syntastic complaints (\ `issue #39 <https://github.com/brokkr/poca/issues/39>`_\ )
* Bug fix: Hangs on feeds without entry size info (\ `issue #40 <https://github.com/brokkr/poca/issues/40>`_\ )
* Bug fix: Crash on entries without enclosures (\ `issue #41 <https://github.com/brokkr/poca/issues/41>`_\ )
* Style: Using named tuples for Outcome (https://pythontips.com/2015/06/06/why-should-you-use-namedtuple-instead-of-a-tuple/)

Version `0.6 <https://github.com/brokkr/poca/issues?q=is%3Aclosed+is%3Aissue+milestone%3A0.6>`_
-----------------------------------------------------------------------------------------------------------


* Limit by number of files (\ `issue #14 </brokkr/poca/issues/14>`_\ )
* Filter entries (\ `issue #29 </brokkr/poca/issues/29>`_\ )
* From the top: Option to start podcast from the beginning (\ `issue #28 </brokkr/poca/issues/28>`_\ )
* Cover.jpg: Download cover image from feed (\ `issue #25 </brokkr/poca/issues/25>`_\ )
* Testing for unicode exceptions in feed treatment and mp3 metadata (\ `issue #17 </brokkr/poca/issues/17>`_\ )
* ``max_mb`` has been deprecated in favour of ``max_number``
* Spoofed ``useragent`` introduced as fallback if urllib is denied

Version 0.5
-----------------------------------------------------------------------------------------------------------


* Completed port to Python 3
* Completely revised and simplified stream and log output
* Mp3 tagging reimplemented
* New download function with proper timeouts

Release 0.4
-----------------------------------------------------------------------------------------------------------


* Reduced functionality port to Python3
