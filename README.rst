WDOM
====

.. image:: https://img.shields.io/pypi/v/wdom.svg
   :target: https://pypi.python.org/pypi/wdom

.. image:: https://img.shields.io/pypi/pyversions/wdom.svg
   :target: https://pypi.python.org/pypi/wdom

.. image:: https://readthedocs.org/projects/wdom-py/badge/?version=latest
   :target: http://wdom-py.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/miyakogi/wdom.svg?branch=dev
   :target: https://travis-ci.org/miyakogi/wdom

.. image:: https://codecov.io/github/miyakogi/wdom/coverage.svg?branch=dev
   :target: https://codecov.io/github/miyakogi/wdom?branch=dev

--------------------------------------------------------------------------------

WDOM is a python GUI library for browser-based desktop applications. WDOM
controls HTML elements (DOM) on browser from python, as if it is a GUI element.
APIs are same as browser DOM, but of course, you can write logic codes in
python.

This library includes web-server (`tornado`_/`aiohttp`_), but is not intended to
be used as a web framework, please use for **Desktop** GUI Applications!

Disclaimer
----------

WDOM is in the early development stage, and may contain many bugs. All APIs are
not stable, and may be changed in future release.

Features
--------

* Pure python implementation
* APIs based on `DOM specification`_

  * Not need to learn new special classes/methods for GUI
  * Implemented DOM features are listed in `Wiki page <https://github.com/miyakogi/wdom/wiki/Features>`_

* Theming with CSS frameworks (see `ScreenShots on Wiki <https://github.com/miyakogi/wdom/wiki/ScreenShots>`_)
* JavaScript codes are executable on browser
* Testable with browsers and `Selenium`_ WebDriver
* Licensed under MIT licence

Requirements
------------

Python 3.4.4+ and any modern-browsers are required.
Also supports Electron and PyQt's webkit browsers.
IE is not supported, but most of features will work with IE11 (but not
recomended).

Installation
------------

Install by pip::

    pip install wdom

Or, install latest version from github::

    pip install git+http://github.com/miyakogi/wdom

As WDOM depends on `tornado`_ web framework, it will be installed automatically.
Optionally supports `aiohttp`_, which is a web framework natively supports
asyncio and is partly written in C. Using aiohttp will result in better
performance. If you want to use WDOM with aiohttp, install it with pip::

    pip install aiohttp

Any configurations are not required; when aiohttp is available, WDOM will use it
automatically.

Documents
---------

Document is available `here <http://wdom-py.readthedocs.io/en/latest/>`_.

Example
-------

Simple example:

.. code-block:: python

    import asyncio
    from wdom.document import get_document
    from wdom.server import start_server, stop_server

    if __name__ == '__main__':
        document = get_document()
        h1 = document.createElement('h1')
        h1.textContent = 'Hello, WDOM'
        document.body.appendChild(h1)

        start_server()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            stop_server()

Execute this code and access ``http://localhost:8888`` by browser.
``"Hello, WDOM"`` will shown on the browser.
To stop process, press ``CTRL+C``.

As you can see, methods of WDOM (``document.createElement`` and
``document.body.appendChild``) are very similar to browser JavaScript.

WDOM provides some new DOM APIs (e.g. ``append`` for appending child) and some
tag classes to easily generate elements:

.. code-block:: python

    import asyncio
    from wdom.tag import H1
    from wdom.document import get_document
    from wdom.server import start_server, stop_server

    if __name__ == '__main__':
        document = get_document()
        h1 = H1()
        h1.textContent = 'Hello, WDOM'
        document.body.append(h1)

        start_server()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            stop_server()

Of course, WDOM can handle events:

.. code-block:: python

    import asyncio
    from wdom.tag import H1
    from wdom.server import start_server, stop_server
    from wdom.document import get_document

    if __name__ == '__main__':
        document = get_document()
        h1 = H1('Hello, WDOM', parent=document.body)
        def rev_text(event):
            h1.textContent = h1.textContent[::-1]
        h1.addEventListener('click', rev_text)
        start_server()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            stop_server()

When string ``"Hello, WDOM"`` is clicked, it will be flipped.

Making components with python class:

.. code-block:: python

    import asyncio
    from wdom.tag import Div, H1, Input
    from wdom.server import start_server, stop_server
    from wdom.document import get_document

    class MyApp(Div):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.text = H1('Hello', parent=self)
            self.textbox = Input(parent=self, placeholder='input here...')
            self.textbox.addEventListener('input', self.update)

        def update(self, event):
            self.text.textContent = event.target.value
            # or, you can write as below
            # self.text.textContent = self.textbox.value

    if __name__ == '__main__':
        document = get_document()
        document.body.append(MyApp())
        start_server()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            stop_server()


WDOM package includes some tiny examples. From command line, try::

    python -m wdom.exapmles.rev_text
    python -m wdom.exapmles.data_binding
    python -m wdom.exapmles.timer

Source codes of these examples will be found in `wdom/examples <https://github.com/miyakogi/wdom/tree/dev/wdom/examples>`_.

Contributing
------------

Contributions are welcome!!

If you find any bug, or have any comments, please don't hesitate to report to
`issues on GitHub <https://github.com/miyakogi/wdom/issues>`_.
All your comments are welcome!

.. _DOM specification: https://dom.spec.whatwg.org/
.. _Selenium: http://selenium-python.readthedocs.org/
.. _tornado: http://www.tornadoweb.org/en/stable/
.. _aiohttp: http://aiohttp.readthedocs.org/en/stable/
