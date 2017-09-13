#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Web server control functions."""

import os
import json
import logging
import asyncio
from typing import Any

from tornado import autoreload

from wdom.util import STATIC_DIR
from wdom.options import config
from wdom.server.base import exclude_patterns, open_browser, watch_dir
from wdom.server import _tornado as module

__all__ = (
    'add_static_path',
    'exclude_patterns',
    'get_app',
    'start',
    'start_server',
    'stop_server',
)
logger = logging.getLogger(__name__)
_server = None
server_config = module.server_config
_msg_queue = []


def is_connected() -> bool:
    """Check if the current server has a client connection."""
    return module.is_connected()


def push_message(msg: dict) -> None:
    """Push message on the message queue."""
    _msg_queue.append(msg)


def send_message() -> None:
    """Send message via WS to all client connections."""
    if not _msg_queue:
        return
    msg = json.dumps(_msg_queue)
    _msg_queue.clear()
    for conn in module.connections:
        conn.write_message(msg)


def add_static_path(prefix: str, path: str, no_watch: bool = False) -> None:
    """Add directory to serve static files.

    First argument ``prefix`` is a URL prefix for the ``path``. ``path`` must
    be a directory. If ``no_watch`` is True, any change of the files in the
    path do not trigger restart if ``--autoreload`` is enabled.
    """
    app = get_app()
    app.add_static_path(prefix, path)
    if not no_watch:
        watch_dir(path)


def get_app() -> module.Application:
    """Get root web application object."""
    return module.get_app()


async def _message_loop() -> None:
    while True:
        send_message()
        await asyncio.sleep(config.message_wait)


def start_server(address: str = None, port: int = None,
                 check_time: int = 500, **kwargs: Any) -> module.HTTPServer:
    """Start web server on ``address:port``.

    Use wrapper function :func:`start` instead.

    :arg str address: address of the server [default: localhost].
    :arg int port: tcp port of the server [default: 8888].
    :arg int check_time: millisecondes to wait until reload browser when
        autoreload is enabled [default: 500].
    """
    # Add application's static files directory
    from wdom.document import get_document
    add_static_path('_static', STATIC_DIR)
    doc = get_document()
    if os.path.exists(doc.tempdir):
        add_static_path('tmp', doc.tempdir, no_watch=True)
    if doc._autoreload or config.autoreload or config.debug:
        autoreload.start(check_time=check_time)
    global _server
    _server = module.start_server(address=address, port=port, **kwargs)
    logger.info('Start server on {0}:{1:d}'.format(
        server_config['address'], server_config['port']))

    # start messaging loop
    asyncio.ensure_future(_message_loop())

    if config.open_browser:
        open_browser('http://{}:{}/'.format(server_config['address'],
                                            server_config['port']),
                     config.browser)
    return _server


def stop_server(server: module.HTTPServer = None) -> None:
    """Terminate web server."""
    module.stop_server(server or _server)


def start(**kwargs: Any) -> None:
    """Start web server.

    Run until ``Ctrl-c`` pressed, or if auto-shutdown is enabled, until when
    all browser windows are closed.

    This function accepts keyword areguments same as :func:`start_server` and
    all arguments passed to it.
    """
    start_server(**kwargs)
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
