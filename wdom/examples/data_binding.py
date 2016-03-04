#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom.tag import H1, Div, Input, TextArea
from wdom.document import get_document


class Check(Input):
    type_ = 'checkbox'


def sample_page():
    app = Div()
    textbox = Input(parent=app)
    check1 = Check(parent=app)
    check2 = Check(parent=app)
    textarea = TextArea(parent=app)
    text = H1(parent=app)
    textbox.setAttribute('type', 'text')
    text.text = 'Hello!'

    def update(data):
        text.textContent = textbox.getAttribute('value')

    textbox.addEventListener('input', update)

    page = get_document(app=app, autoreload=True)

    return page
