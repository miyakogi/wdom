#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom.themes.default import H1, Div, Input


class App(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = H1(parent=self)
        self.text.textContent = 'Hello!'
        self.textbox = Input(parent=self)
        self.textbox.setAttribute('type', 'text')
        self.textbox.addEventListener('input', self.update)

    def update(self, event):
        self.text.textContent = self.textbox.getAttribute('value')


def sample_app(**kwargs):
    return App()


if __name__ == '__main__':
    import asyncio
    from wdom.document import get_document
    from wdom import server
    document = get_document()
    document.body.prepend(sample_app())
    server.start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    server.stop_server()
