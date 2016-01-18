#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.dom import Node
from wdom.view import get_document


class App(Node):
    tag = 'sci-app'


class H1(Node):
    tag = 'h1'


def sample_page() -> Node:
    app = App()
    text = H1(parent=app)
    text.text = 'Click!'

    def reverse(data):
        text.textContent = text.textContent[::-1]

    text.addEventListener('click', reverse)

    page = get_document(app=app)

    return page
