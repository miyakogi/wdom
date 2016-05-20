Loading Static Contents
-----------------------

Contents on the Web
^^^^^^^^^^^^^^^^^^^

As an example, use `bootstrap`_.

To use bootstrap, one css file (bootstrap.min.css) and two js files (jquery and
bootstrap.min.js) are need to be loaded.
To load css file, use ``<link>`` tag and insert into the ``<head>``.
And to load js files, use ``<script>`` tag and insert into the ``<body>``.
Both ``<head>`` and ``<body>`` tags can be accessed via ``document.head`` and
``document.body`` (same as JavaScript).

.. literalinclude:: samples/static1.py

As frequently required to load css and js files on document, WDOM provides
shortcut method; ``document.add_cssfile({/path/to/cssfile})`` and
``document.add_jsfile({/path/to/jsfile})``.

.. literalinclude:: samples/static2.py

Local Resources
^^^^^^^^^^^^^^^

User's css files and other static contents, like images or html files, are also
available on WDOM app.

For the directory tree like below::

    .
    ├── static
    │   └── css
    │       └── app.css
    ├── app.py
    ├── module1.py
    ├── ...
    ...

When want to use ``static/css/app.css`` from ``app.py``, ``app.py`` will become
as follows:

.. literalinclude:: samples/static3.py

The first argument of the ``add_static_path`` is a prefix to access the
static files and the second argument is a path to the directory to be served.
Files under the assigned directory can be accessed by URL like
``http://localhost:8888/prefix/(dirname/)filename``.
For example, if accessed to ``http://localhost:8888/static/css/app.css`` with a
browser, ``app.css`` will be shown.

It's not necessary to use the same name for the prefix as the directory name to
be registered.
For example, in case to use ``my_static`` as a prefix, change to
``add_static_path('my_static', static_dir)`` and then can be accessed to
``app.css`` from ``http://localhost:8888/my_static/css/app.css``.

Not only css files but also any static files, like js files, html files, or
images are able to be served.

Any prefixes can be used if it is valid for URL, but ``_static`` and ``tmp`` is
already used by WDOM internally, so do not use them for a prefix.

.. _bootstrap: http://getbootstrap.com/
