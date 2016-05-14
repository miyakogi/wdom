#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from wdom.document import get_document
from wdom.server import start_server, stop_server


if __name__ == '__main__':
    document = get_document()
    h1 = document.createElement('h1')
    h1.textContent = 'Hello, WDOM'
    document.body.appendChild(h1)

    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
