#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from os import path

from wdom.misc import install_asyncio
from wdom.document import get_document
from wdom.server import get_app, start_server, stop_server
from wdom.tag import Button


if __name__ == '__main__':
    install_asyncio()

    static_dir = path.join(path.dirname(path.abspath(__file__)), 'static')
    document = get_document()
    document.add_cssfile('/static/css/app.css')

    # Add <link>-tag sourcing bootstrap.min.css on <head>

    # Add button element
    document.body.appendChild(Button('click'))

    app = get_app(document)
    app.add_static_path('static', static_dir)
    loop = asyncio.get_event_loop()
    server = start_server(app, port=8888, loop=loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        stop_server(server)
