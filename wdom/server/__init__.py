#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import importlib
from typing import Optional

from tornado import autoreload

from wdom.misc import static_dir, install_asyncio
from wdom.options import config
from wdom.document import get_document
from wdom.server.base import exclude_patterns, open_browser, watch_dir

try:
    from wdom.server import _aiohttp as module
except ImportError:
    from wdom.server import _tornado as module

__all__ = ('get_app', 'start_server', 'stop_server', 'exclude_patterns')
logger = logging.getLogger(__name__)


def add_static_path(prefix, path, no_watch: bool = False):
    app = get_app()
    app.add_static_path(prefix, path)
    if not no_watch:
        watch_dir(path)


def get_app(*args, **kwargs):
    return module.get_app()


def set_server_type(type):
    global module
    if type == 'aiohttp':
        module = importlib.import_module('wdom.server._aiohttp')
    elif type == 'tornado':
        module = importlib.import_module('wdom.server._tornado')


main_server = None


def start_server(app: Optional[module.Application] = None,
                 browser: Optional[str] = None,
                 address: Optional[str] = None,
                 check_time: Optional[int] = 500,
                 **kwargs):
    # Add application's static files directory
    add_static_path('_static', static_dir)
    doc = get_document()
    if os.path.exists(doc.tempdir):
        add_static_path('tmp', doc.tempdir, no_watch=True)
    if doc._autoreload:
        install_asyncio()
        autoreload.start(check_time=check_time)
    global main_server
    main_server = module.start_server(**kwargs)
    logger.info('Start server on {0}:{1:d}'.format(
        main_server.address, main_server.port))

    if config.open_browser:
        open_browser(
            'http://{}:{}/'.format(main_server.address, main_server.port),
            browser or config.browser)
    return main_server


def stop_server(server=None):
    module.stop_server(server or main_server)
