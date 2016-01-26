#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from markdown import markdown

from wdom.document import get_document
from wdom.dom import Div
from wdom.themes.bootstrap3 import css_files, js_files
from wdom.themes.bootstrap3 import TextArea, Col6, Row, H1, Hr


class Editor(Row):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('style', 'height: 80vh;')
        editor_col = Col6(parent=self)
        viewer_col = Col6(parent=self)
        self.editor = TextArea(parent=editor_col)
        self.editor.setAttribute('style', 'height: 80vh')
        self.viewer = Div(parent=viewer_col)
        self.viewer.setAttribute(
            'style',
            '''
            height: 100%;
            min-height: 80vh;
            padding: 0 2em;
            border: 1px solid #ddd;
            border-radius: 3px;
            ''',
        )

        self.editor.addEventListener('input', self.render)
        self.editor.addEventListener('change', self.render)

    def render(self, data):
        html = markdown(data['value'])
        self.viewer.innerHTML = html


def sample_page():
    doc = get_document()
    for js in js_files:
        doc.add_jsfile(js)
    for css in css_files:
        doc.add_cssfile(css)
    app = Div(parent=doc.body, style='width: 90vw; margin: auto')
    title = H1('Simple Markdown Editor', class_='text-center')
    app.appendChild(title)
    app.appendChild(Hr())
    app.appendChild(Editor())
    return doc
