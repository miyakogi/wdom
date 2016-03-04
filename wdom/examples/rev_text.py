#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import H1, Div
from wdom.document import get_document


def sample_page() -> Div:
    app = Div()
    text = H1(parent=app)
    text.textContent = 'Click!'

    def reverse(data):
        text.textContent = text.textContent[::-1]

    text.addEventListener('click', reverse)

    page = get_document(app=app, autoreload=True)

    return page
