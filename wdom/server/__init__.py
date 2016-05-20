#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import importlib
from typing import Optional

from tornado import autoreload

from wdom.misc import static_dir, install_asyncio
from wdom.options import config
from wdom.server.base import exclude_patterns, open_browser, watch_dir

logger = logging.getLogger(__name__)

try:
    import aiohttp
    v = aiohttp.__version__.split('.')
    if int(v[0]) > 0 or int(v[1]) >= 21:
        from wdom.server import _aiohttp as module
    else:
        logger.warning(
            'wdom requires aiohttp >= 0.21.0, but {} is installed. '
            'please update it by `pip install -U aiohttp.'.format(
                aiohttp.__version__)
        )
        raise ImportError
except ImportError:
    from wdom.server import _tornado as module

__all__ = ('get_app', 'start_server', 'stop_server', 'exclude_patterns')
_server = None


def is_connected():
    """Check if the current server has a client connection."""
    return module.is_connected()


def send_message(msg: str):
    """Send message to all client connections."""
    for conn in module.connections:
        conn.write_message(msg)


def add_static_path(prefix, path, no_watch: bool = False):
    """Add directory to serve static files.

    First argument ``prefix`` is a URL prefix for the ``path``. ``path`` must
    be a directory. If ``no_watch`` is True, any change of the files in the
    path do not trigger restart if ``--autoreload`` is enabled.
    """
    app = get_app()
    app.add_static_path(prefix, path)
    if not no_watch:
        watch_dir(path)


def get_app(*args, **kwargs):
    """Get root Application object."""
    return module.get_app()


def set_server_type(type):
    """Set server type to document and handle websocket connection.

    By default, if aiohttp is available wdom uses aiohttp for server. Otherwise
    use tornado.
    """
    global module
    if type == 'aiohttp':
        module = importlib.import_module('wdom.server._aiohttp')
    elif type == 'tornado':
        module = importlib.import_module('wdom.server._tornado')
    else:
        raise ValueError(
            '{0} is not supported now. Available server types are:'
            ' aiohttp, tornado'.format(type)
        )


def start_server(app: Optional[module.Application] = None,
                 browser: Optional[str] = None,
                 address: Optional[str] = None,
                 check_time: Optional[int] = 500,
                 **kwargs):
    """Start web server."""
    # Add application's static files directory
    from wdom.document import get_document
    add_static_path('_static', static_dir)
    doc = get_document()
    if os.path.exists(doc.tempdir):
        add_static_path('tmp', doc.tempdir, no_watch=True)
    if doc._autoreload or config.autoreload or config.debug:
        install_asyncio()
        autoreload.start(check_time=check_time)
    global _server
    _server = module.start_server(**kwargs)
    logger.info('Start server on {0}:{1:d}'.format(
        _server.address, _server.port))

    if config.open_browser:
        open_browser('http://{}:{}/'.format(_server.address, _server.port),
                     browser or config.browser)
    return _server


def stop_server(server=None):
    """Terminate web server."""
    module.stop_server(server or _server)
