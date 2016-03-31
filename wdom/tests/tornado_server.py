#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os.path import dirname, abspath
import asyncio

from tornado.platform.asyncio import AsyncIOMainLoop
AsyncIOMainLoop().install()

root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from wdom import options
from wdom.document import get_document
from wdom.server_tornado import start_server, stop_server, get_app

options.parse_command_line()
loop = asyncio.get_event_loop()
app = get_app(get_document())
server = start_server(app, loop=loop)
try:
    loop.run_forever()
except Exception:
    stop_server(server)
    loop.stop()
