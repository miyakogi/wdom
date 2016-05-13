#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from wdom.server import start_server, stop_server
from wdom.document import get_document


if __name__ == '__main__':
    document = get_document()
    h1 = document.createElement('h1')
    h1.textContent = 'Hello, WDOM'
    input = document.createElement('textarea')
    def update(event):
        h1.textContent = event.target.value
    input.addEventListener('input', update)
    document.body.appendChild(input)
    document.body.appendChild(h1)

    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
