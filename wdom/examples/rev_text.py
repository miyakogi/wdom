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
    from wdom.document import set_app
    from wdom import server
    set_app(sample_app())
    server.start()
