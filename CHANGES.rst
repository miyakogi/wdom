Version 0.2
-----------

(next version)

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
