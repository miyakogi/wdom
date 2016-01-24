#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from typing import Optional

import pystache
from wdom.options import config
from wdom.misc import template_dir
from wdom.dom import Text, RawHtmlNode
from wdom.dom.node import Node

import logging
logger = logging.getLogger(__name__)


class Document:
    def __init__(self, app=None, title: str = 'W-DOM',
                 charset: str = 'utf-8',
                 autoreload: bool = False,
                 reload_wait: int = 500,  # unit: msec
                 template_file: str = None,
                 ):
        self.contents = []
        self.components = {}

        self.jsfiles = []
        self.cssfiles = []
        self.headers = []

        self.config = dict(
            title=title,
            charset=charset,
            autoreload=autoreload,
            reload_wait=reload_wait,
        )

        if template_file is None:
            self.template_file = path.join(template_dir, 'page.mustache')
        else:
            self.template_file = template_file

        if app is not None:
            self.set_body(app)

    def add_jsfile(self, jsfile: str):
        self.jsfiles.append(jsfile)

    def add_cssfile(self, cssfile: str):
        self.cssfiles.append(cssfile)

    def add_header(self, string: str):
        self.headers.append(string)

    def set_body(self, content):
        if isinstance(content, Node):
            self.contents.append(content)
            content.parent = self
        elif isinstance(content, str):
            html = RawHtmlNode(content)
            self.contents.append(html)
            html.parent = self
        else:
            raise TypeError('Get invalid type object: {}'.format(content))

    def build(self) -> str:
        with open(self.template_file) as f:
            template = f.read()

        contents = []
        for content in self.contents:
            if isinstance(content, str):
                contents.append({'content': content})
            elif isinstance(content, Node):
                contents.append({'content': content.html})
            else:
                raise TypeError('Invalid type object in body: {}'.format(content))

        config = {
            'contents': contents,
            'jsfiles': [{'js': js} for js in self.jsfiles],
            'cssfiles': [{'css': css} for css in self.cssfiles],
            'headers': [{'header': header} for header in self.headers],
        }
        config.update(self.config)

        html = pystache.render(template, config)
        return html


def get_document(include_wdom: bool = True,
                 include_skeleton: bool = False,
                 include_normalizecss: bool = False,
                 autoreload: Optional[bool] = None,
                 app: Optional[Text] = None,
                 **kwargs
                 ) -> Document:

    if autoreload is None:
        if 'autoreload' in config:
            autoreload = config.autoreload
        if 'debug' in config:
            autoreload = config.debug

    document = Document(app=app, autoreload=autoreload, **kwargs)

    if include_wdom:
        document.add_jsfile('_static/js/wdom.js')

    return document
