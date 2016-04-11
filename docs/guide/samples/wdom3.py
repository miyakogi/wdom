#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from wdom.misc import install_asyncio  # only when using tornado
from wdom.server import get_app, start_server, stop_server
from wdom.document import get_document
from wdom.tag import Div, H1, Input


class MyElement(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h1 = H1('Hello, WDOM', parent=self)  
        self.input = Input(parent=self)
        self.input.addEventListener('input', self.update)

    def update(self, event):
        self.h1.textContent = event.target.value


if __name__ == '__main__':
    install_asyncio()  # only when using tornado

    document = get_document()
    document.body.appendChild(MyElement())

    app = get_app(document)
    loop = asyncio.get_event_loop()
    server = start_server(app, port=8888, loop=loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        stop_server(server)
