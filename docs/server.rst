Application and Server
======================

WDOM supports two web-server library, tornado and aiohttp.
tornado is required to use WDOM, but aiohttp is optional.

tornado is written in pure-python, so it works well in any environment.
aiohttp is implemented with C-extention, and natively asyncio friendly.

WDOM server module is provided by ``wdom.server``. If aiohttp is available, wdom
will use it. This module wraps web-servers, tornado or aiohttp, so users don't
need to care which server is used now.

.. automodule:: wdom.server

   .. autofunction:: add_static_path

   .. autofunction:: start_server

   .. autofunction:: stop_server
