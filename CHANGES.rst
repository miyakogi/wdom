Version 0.2
-----------

(next version)

* Drop python 3.4 support (in plan)

Version 0.1.8 (not released)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Improve HTML parsing
* Don't send events to unmounted DOM

Version 0.1.7 (2017-07-21)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Update PyPI metadata
* Add shortcut functions (``server.start()`` and ``document.set_app()``)

Version 0.1.6 (2017-07-21)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Drop aiohttp support

Version 0.1.5 (2017-06-03)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Tentatively disable aiohttp
* Catch up recent updates
* Add Concise CSS

Version 0.1.4 (2016-05-20)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Examples are executable by one file
* Upload document to readthedocs

Version 0.1.3 (2016-05-17)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* (bug fix) Add dependency of mypy-lang for python < 3.5

Version 0.1.2 (2016-05-15)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``TestCase.wait`` methods take two argument, ``timeout`` and ``times``.
* Add ``wait_until`` method and ``timeout`` class variable on ``TestCase``.
* Default value of ``TestCase.wait_time`` is same as local and travis ci. If
  longer wait time is required on travis, change ``wait_time`` on each test
  case.
* Support access log on aiohttp server

Version 0.1.1 (2016-05-15)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* minor update on meta data

Version 0.1 (2016-05-15)
------------------------

First public release.
