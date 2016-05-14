#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))

from xml.etree.ElementTree import HTML_EMPTY
from html.parser import HTMLParser

from wdom.document import Document
from wdom.node import DocumentFragment, Comment
from wdom.web_node import WebElement


class DocumentParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            elm = WebElement(tag, parent=self.elm, **dict(attrs))
            if self.elm:
                self.elm.append(elm)
            if tag not in HTML_EMPTY:
                self.elm = elm

    def handle_endtag(self, tag):
        self.elm = self.elm.parentNode

    def handle_data(self, data):
        _d = data.strip()
        if _d and self.elm:
            self.elm.append(_d)

    def handle_comment(self, comment:str):
        self.elm.append(Comment(comment))


class FragmentParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elm = DocumentFragment()
        self.root = self.elm

    def handle_starttag(self, tag, attrs):
        elm = WebElement(tag, parent=self.elm, **dict(attrs))
        if self.elm:
            self.elm.append(elm)
        if tag not in HTML_EMPTY:
            self.elm = elm

    def handle_endtag(self, tag):
        self.elm = self.elm.parentNode

    def handle_data(self, data):
        if data and self.elm:
            self.elm.append(data)

    def handle_comment(self, comment:str):
        self.elm.append(Comment(comment))


def parse_document(doc:str):
    parser = DocumentParser()
    parser.feet(doc)
    return parser.root


def parse_html(html:str):
    parser = FragmentParser()
    parser.feed(html)
    return parser.root
