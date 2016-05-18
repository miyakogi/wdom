#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.themes.default import H1, Div


class App(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = H1('Click!', parent=self)
        self.text.addEventListener('click', self.reverse)

    def reverse(self, event):
        self.text.textContent = self.text.textContent[::-1]


def sample_app(**kwargs) -> Div:
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
