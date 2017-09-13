Application and Server
======================

WDOM applications consist of a single html :py:class:`Document` and a web server.


HTML Document Object
--------------------

.. currentmodule:: wdom.document

.. autoclass:: wdom.document.WdomDocument
   :members:

.. autofunction:: wdom.document.get_new_document

.. autofunction:: wdom.document.get_document

.. autofunction:: wdom.document.set_document


Web Server
----------

.. currentmodule:: wdom.server

.. automodule:: wdom.server

   .. autofunction:: add_static_path

   .. autofunction:: start

   .. autofunction:: get_app

   .. autofunction:: start_server

   .. autofunction:: stop_server
