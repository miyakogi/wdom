#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from wdom.options import config
from wdom.dom.node import Node, DocumentType, Text
from wdom.dom import Html, Head, Body, Meta, Link, Title, Script, RawHtml


class Document(Node):
    nodeType = Node.DOCUMENT_NODE
    nodeName = '#document'

    def __init__(self, doctype='html', title='W-DOM', charset='utf-8'):
        super().__init__()
        self.connections = []
        self.doctype = DocumentType(doctype)
        self.appendChild(self.doctype)

        self.html = Html(parent=self)

        self.head = Head(parent=self.html)
        self.charset_element = Meta(parent=self.head)
        self.charset = charset
        self.title_element = Title(parent=self.head)
        self.title = title

        self.body = Body(parent=self.html)
        self.script = Script(parent=self.body)

    @property
    def title(self) -> str:
        return self.title_element.textContent

    @title.setter
    def title(self, value:str):
        self.title_element.textContent = value

    @property
    def charset(self) -> str:
        return self.charset_element.getAttribute('charset')

    @charset.setter
    def charset(self, value:str):
        self.charset_element.setAttribute('charset', value)

    def add_jsfile(self, src:str):
        self.body.appendChild(Script(src=src))

    def add_cssfile(self, src:str):
        self.head.appendChild(Link(rel='stylesheet', href=src))

    def add_header(self, header:str):
        self.head.appendChild(RawHtml(header))

    def set_body(self, node:Node):
        if isinstance(node, (str, bytes)):
            node = Text(node)
        self.body.insertBefore(node, self.body.firstChild)

    def build(self) -> str:
        return ''.join(child.html for child in self.childNodes)


def get_document(include_wdom: bool = True,
                 include_skeleton: bool = False,
                 include_normalizecss: bool = False,
                 autoreload: Optional[bool] = None,
                 app: Optional[Node] = None,
                 **kwargs
                 ) -> Document:

    if autoreload is None:
        if 'autoreload' in config:
            autoreload = config.autoreload
        if 'debug' in config:
            autoreload = config.debug

    document = Document()
    if app is not None:
        document.body.appendChild(app)

    script = '\n'
    if autoreload:
        script += 'var WDOM_AUTORELOAD = true\n'
    document.script.textContent = script

    if include_wdom:
        document.add_jsfile('_static/js/wdom.js')

    return document
