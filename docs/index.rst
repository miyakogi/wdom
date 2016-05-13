.. WDOM documentation master file, created by
   sphinx-quickstart on Mon Jan 11 18:49:13 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

WDOM
====

WDOM is a library to control DOM on browser, as if it is a GUI element. This
library includes web-server (tornado/aiohttp), but is not intended to be used as
a web framework, please use for **Desktop** GUI Applications!

Features
--------

* Pure python implementation
* Theming with CSS frameworks
* `DOM specification`_ based API

  * Not need to learn new special classes/methods
  * Implemented DOM features are listed in `Wiki page <https://github.com/miyakogi/wdom/wiki/Features>`_

* Testable with browsers and `Selenium`_ WebDriver
* Licensed under MIT licence

Requirements
------------

Python 3.5.1+ and any modern-browsers are required.
Also supports Electron and PyQt's webkit browsers.
IE is not supported, but most of features will work with IE11 (but not
recomended).

Installation
------------

Install from github by pip::

    pip install git+http://github.com/miyakogi/wdom

As WDOM depends on `tornado`_ web framework, it will be installed automatically.
Optionally supports `aiohttp`_, which is a web framework natively supports
asyncio and is partly written in C. Using aiohttp will result in better
performance. If you want to use WDOM with aiohttp, install it with pip::

    pip install aiohttp

Any configurations are not required; when aiohttp is available, WDOM will use it
automatically.

Contents
--------

.. toctree::
    :titlesonly:

    guide/index
    dom
    server
    test


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _DOM specification: https://dom.spec.whatwg.org/
.. _Selenium: http://selenium-python.readthedocs.org/
.. _tornado: http://www.tornadoweb.org/en/stable/
.. _aiohttp: http://aiohttp.readthedocs.org/en/stable/
