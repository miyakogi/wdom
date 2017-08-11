WDOM
====

.. image:: https://img.shields.io/pypi/v/wdom.svg
   :target: https://pypi.python.org/pypi/wdom

.. image:: https://img.shields.io/pypi/pyversions/wdom.svg
   :target: https://pypi.python.org/pypi/wdom

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: https://miyakogi.github.io/wdom/
   :alt: Documentation

.. image:: https://travis-ci.org/miyakogi/wdom.svg?branch=dev
   :target: https://travis-ci.org/miyakogi/wdom

.. image:: https://codecov.io/github/miyakogi/wdom/coverage.svg?branch=dev
   :target: https://codecov.io/github/miyakogi/wdom?branch=dev

--------------------------------------------------------------------------------

WDOM is a python GUI library for browser-based desktop applications. WDOM
controls HTML elements (DOM) on browser from python, as if it is a GUI element.
APIs are same as DOM or browser JavaScript, but of course, you can write logic
codes in python.

This library includes web-server (`tornado`_), but is not intended to
be used as a web framework, please use for **Desktop** GUI Applications.

Document: `WDOM Documentation <https://miyakogi.github.io/wdom/>`_

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

Python 3.5.3+ and any modern-browsers are required.
Also supports Electron and PyQt's webkit browsers.

Installation
------------

Install by pip::

    pip install wdom

Or, install latest version from github::

    pip install git+http://github.com/miyakogi/wdom

Example
-------

Simple example:

.. code-block:: python

    from wdom.document import get_document
    from wdom.server import start

    if __name__ == '__main__':
        document = get_document()
        h1 = document.createElement('h1')
        h1.textContent = 'Hello, WDOM'
        document.body.appendChild(h1)
        start()

Execute this code and access ``http://localhost:8888`` by browser.
``"Hello, WDOM"`` will shown on the browser.
To stop process, press ``CTRL+C``.

As you can see, methods of WDOM (``document.createElement`` and
``document.body.appendChild``) are very similar to browser JavaScript.

WDOM provides some new DOM APIs (e.g. ``append`` for appending child) and some
tag classes to easily generate elements:

.. code-block:: python

    from wdom.tag import H1
    from wdom.document import set_app
    from wdom.server import start

    if __name__ == '__main__':
        h1 = H1()
        h1.textContent = 'Hello, WDOM'
        set_app(h1) # equivalent to `wdom.document.get_document().body.appendChild(h1)`
        start()

Of course, WDOM can handle events:

.. code-block:: python

    from wdom.tag import H1
    from wdom.document import set_app
    from wdom.server import start

    def rev_text(event):
        elm = event.currentTarget
        elm.textContent = elm.textContent[::-1]

    if __name__ == '__main__':
        h1 = H1('Hello, WDOM')
        h1.addEventListener('click', rev_text)
        set_app(h1)
        start()

When string ``"Hello, WDOM"`` is clicked, it will be flipped.

Making components with python class:

.. code-block:: python

    from wdom.tag import Div, H1, Input
    from wdom.document import set_app
    from wdom.server import start

    class MyApp(Div):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.text = H1('Hello', parent=self)
            self.textbox = Input(parent=self, placeholder='input here...')
            self.textbox.addEventListener('input', self.update)

        def update(self, event):
            self.text.textContent = event.currentTarget.value
            # Or, you can write as below
            # self.text.textContent = self.textbox.value

    if __name__ == '__main__':
        set_app(MyApp())
        start()


WDOM package includes some tiny examples. From command line, try::

    python -m wdom.exapmles.rev_text
    python -m wdom.exapmles.data_binding
    python -m wdom.exapmles.timer

Source codes of these examples will be found in `wdom/examples <https://github.com/miyakogi/wdom/tree/dev/wdom/examples>`_.

Theming with CSS Frameworks
---------------------------

WDOM is CSS friendly, and provides easy way to theme your app with CSS
frameworks. For example, use bootstrap3:

.. code-block:: python

    from wdom.themes import bootstrap3
    from wdom.themes.bootstrap3 import Button, PrimaryButton, DangerButton
    from wdom.document import get_document
    from wdom.server import start

    if __name__ == '__main__':
        document = get_document()
        document.register_theme(bootstrap3)
        document.body.append(
            Button('Button'), PrimaryButton('Primary'), DangerButton('Danger')
        )
        start()

Differences are:

- import tag classes from ``wdom.themes.[theme_name]`` instead of ``wdom.tag``
- register theme-module by ``document.register_theme(theme_module)``

If you want to more easily change themes (or, css frameworks), try command-line
option ``--theme``. ``wdom.themes.default`` module would be switched to
``--theme`` option.

For example, in the above code, change ``from wdom.themes import bootstrap3`` to
``from wdom.themes import default``. And execute the code with ``--theme
theme_name`` option (see below).


.. image:: https://raw.githubusercontent.com/wiki/miyakogi/wdom/screencasts/themes.gif
   :target: https://raw.githubusercontent.com/wiki/miyakogi/wdom/screencasts/themes.gif
   :width: 90%


Currently, WDOM bundles 20+ CSS frameworks by default, and they are listed in
`Wiki <https://github.com/miyakogi/wdom/wiki/ScreenShots>`_ with screenshots. In
each theme module, only primitive HTML elements (typographies, buttons, form
components, tables, and grids) are defined, but complex elements like
navigations or tabs are not defined.

If your favourite CSS framework is not included, please let me know on `Issues`_,
or write its wrapper module and send `PR`_.

Of course you can use your original css. See `Loading Static Contents -> Local
Resource
<https://miyakogi.github.io/wdom/guide/load_resource.html#local-resources>`_
section in the `User Guide`_.

Contributing
------------

Contributions are welcome!!

If you find any bug, or have any comments, please don't hesitate to report to
`Issues`_ on GitHub.
All your comments are welcome!

More Documents
--------------

Please see `User Guide`_.

.. _DOM specification: https://dom.spec.whatwg.org/
.. _Selenium: http://selenium-python.readthedocs.org/
.. _tornado: http://www.tornadoweb.org/en/stable/
.. _User Guide: https://miyakogi.github.io/wdom/guide/index.html
.. _Issues: https://github.com/miyakogi/wdom/issues
.. _PR: https://github.com/miyakogi/wdom/pulls
