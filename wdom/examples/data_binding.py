#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom.tag import H1, Div, Input
from wdom.document import get_document


class Check(Input):
    type_ = 'checkbox'


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


def sample_page(**kwargs):
    page = get_document(**kwargs)
    page.body.prepend(App())
    return page
