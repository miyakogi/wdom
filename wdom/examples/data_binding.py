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
    from wdom.document import set_app
    from wdom import server
    set_app(sample_app())
    server.start()
