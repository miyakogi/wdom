#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from wdom.misc import install_asyncio #  only when using tornado
from wdom.server import get_app, start_server, stop_server
from wdom.document import get_document


if __name__ == '__main__':
    install_asyncio() #  only when using tornado

    document = get_document()
    h1 = document.createElement('h1')
    h1.textContent = 'Hello, WDOM'
    input = document.createElement('textarea')
    def update(event):
        h1.textContent = event.target.value
    input.addEventListener('input', update)
    document.body.appendChild(input)
    document.body.appendChild(h1)

    app = get_app(document)
    loop = asyncio.get_event_loop()
    server = start_server(app, port=8888, loop=loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        stop_server(server)
