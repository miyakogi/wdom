#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom.tag import Node, Input, TextArea
from wdom.view import get_document


class App(Node):
    tag = 'wdom-app'


class H1(Node):
    tag = 'h1'

class Check(Input):
    type_ = 'checkbox'

def sample_page() -> Node:
    app = App()
    textbox = Input(parent=app)
    check1 = Check(parent=app)
    check2 = Check(parent=app)
    textarea = TextArea(parent=app)
    text = H1(parent=app)
    textbox.setAttribute('type', 'text')
    text.text = 'Hello!'

    def update(data):
        text.textContent = textbox.getAttribute('value')

    # textbox.addEventListener('input', update)

    page = get_document(app=app)

    return page
