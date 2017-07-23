#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import HTML_EMPTY
from html.parser import HTMLParser


class FragmentParser(HTMLParser):
    default_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from wdom.node import DocumentFragment
        self.elm = DocumentFragment()
        self.root = self.elm

    def handle_starttag(self, tag, attr):
        from wdom.document import create_element
        attrs = dict(attr)
        params = dict(parent=self.elm, **attrs)
        elm = create_element(tag, attrs.get('is'), self.default_class, params)
        if self.elm:
            self.elm.append(elm)
        if tag not in HTML_EMPTY:
            self.elm = elm

    def handle_endtag(self, tag):
        self.elm = self.elm.parentNode

    def handle_data(self, data):
        if data and self.elm:
            self.elm.append(data)

    def handle_comment(self, comment: str):
        from wdom.node import Comment
        self.elm.append(Comment(comment))


class DocumentParser(FragmentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from wdom.document import Document
        self.root = Document()
        self.elm = self.root.body

    def handle_decl(self, decl):
        if decl.startswith('DOCTYPE'):
            self.root.doctype.name = decl.split()[-1]

    def handle_starttag(self, tag, attrs):
        if tag == 'html':
            self.elm = self.root.html
        elif tag == 'head':
            self.elm = self.root.head
        elif tag == 'body':
            self.elm = self.root.body
        else:
            super().handle_starttag(tag, attrs)


def parse_document(doc: str):
    parser = DocumentParser()
    parser.feet(doc)
    return parser.root


def parse_html(html: str):
    parser = FragmentParser()
    parser.feed(html)
    return parser.root
