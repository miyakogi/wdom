#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from wdom.server import start_server, stop_server
from wdom.document import get_document
from wdom.tag import Div, H1, Input


class MyElement(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h1 = H1()
        self.h1.textContent = 'Hello, WDOM'
        self.input = Input()
        self.input.addEventListener('input', self.update)
        self.appendChild(self.input)
        self.appendChild(self.h1)

    def update(self, event):
        self.h1.textContent = event.target.value


if __name__ == '__main__':
    document = get_document()
    document.body.appendChild(MyElement())
    server = start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
