#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from wdom.document import get_document
from wdom.server import start_server, stop_server
from wdom.themes.default import Div, H1, Container
from wdom.themes.default import PrimaryButton, DangerButton, DefaultButton


class Timer(Container):
    def __init__(self, *args, **kwargs):
        self._running = False
        self._count = 180
        self._interval = 0.01
        self._loop = asyncio.get_event_loop()
        super().__init__(*args, **kwargs)
        self._view = H1(parent=self)
        self.update()
        self._start_btn = PrimaryButton('start', parent=self, id='start_btn')
        self._start_btn.addEventListener('click', self.start)
        self._stop_btn = DangerButton('stop', parent=self, id='stop_btn')
        self._stop_btn.addEventListener('click', self.stop)
        self._reset_btn = DefaultButton('reset', parent=self, id='reset_btn')
        self._reset_btn.addEventListener('click', self.reset)

    def stop(self, event):
        self._running = False

    def start(self, event):
        self._running = True
        self._timer_loop()

    def reset(self, event):
        self._count = 180
        self.update()

    def _timer_loop(self):
        if self._running and self._count > 0:
            self._loop.call_later(self._interval, self._timer_loop)
            self._count -= self._interval
            self.update()

    def set(self, value):
        self._view.textContent = '{0:.2f}'.format(value)

    def update(self):
        self.set(self._count)


def sample_page(**kwargs) -> Div:
    app = Timer()
    page = get_document(**kwargs)
    page.body.prepend(app)
    return page


if __name__ == '__main__':
    from wdom.themes import default
    doc = sample_page()
    doc.register_theme(default)
    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_server()
