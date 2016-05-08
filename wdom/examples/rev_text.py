#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import H1, Div
from wdom.document import get_document


def sample_page(**kwargs) -> Div:
    app = Div()
    text = H1(parent=app)
    text.textContent = 'Click!'

    def reverse(event):
        text.textContent = text.textContent[::-1]

    text.addEventListener('click', reverse)

    page = get_document(**kwargs)
    page.body.prepend(app)

    return page
