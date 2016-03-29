#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom.tag import H1, Div, Input
from wdom.document import get_document


class Check(Input):
    type_ = 'checkbox'


def sample_page(**kwargs):
    app = Div()
    textbox = Input(parent=app)
    text = H1(parent=app)
    textbox.setAttribute('type', 'text')
    text.textContent = 'Hello!'

    def update(event):
        text.textContent = textbox.getAttribute('value')

    textbox.addEventListener('input', update)

    page = get_document(app=app, **kwargs)

    return page
