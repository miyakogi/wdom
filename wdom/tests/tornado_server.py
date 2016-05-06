#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os.path import dirname, abspath, join
import asyncio

root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from wdom.misc import install_asyncio
from wdom import options
from wdom.document import get_document
from wdom.server_tornado import start_server, stop_server, get_app

install_asyncio()
options.parse_command_line()
loop = asyncio.get_event_loop()
doc = get_document()
with open(join(doc.tempdir, 'a.html'), 'w') as f:
    f.write(doc.tempdir)
app = get_app(doc)
server = start_server(app, loop=loop)
try:
    loop.run_forever()
except Exception:
    stop_server(server)
    loop.stop()
