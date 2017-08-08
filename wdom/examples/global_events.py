#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom import server
from wdom.document import get_document, set_app
from wdom.tag import H1, Div, Input


def sample_page(**kwargs):
    doc = get_document()
    win = doc.defaultView
    app = Div()
    inp = Input(id='input', parent=app)
    win1 = H1(id='win1', parent=app)
    doc1 = H1(id='doc1', parent=app)
    input_view = H1(id='input_view', parent=app)

    def add_letter_doc(e):
        doc1.textContent = doc1.textContent + e.key

    def add_letter_win(e):
        win1.textContent = win1.textContent + e.key

    def input_handler(e):
        input_view.textContent = e.data

    doc.addEventListener('keypress', add_letter_doc)
    win.addEventListener('keypress', add_letter_win)
    inp.addEventListener('input', input_handler)
    return app


def main():
    set_app(sample_page())
    server.start()


if __name__ == '__main__':
    main()
