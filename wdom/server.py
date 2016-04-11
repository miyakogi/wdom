#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.server_base import exclude_patterns

try:
    from wdom.server_aio import get_app, start_server, stop_server
except ImportError:
    from wdom.server_tornado import get_app, start_server, stop_server

__all__ = ('get_app', 'start_server', 'stop_server', 'exclude_patterns')
