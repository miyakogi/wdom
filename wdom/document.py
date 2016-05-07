#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import atexit
import shutil
from types import ModuleType
from typing import Optional, Union

from wdom.options import config
from wdom.interface import Event
from wdom.node import Node, DocumentType, Text, RawHtml, Comment
from wdom.node import DocumentFragment
from wdom.element import Element, Attr, _create_element
from wdom.web_node import WebElement
from wdom.tag import HTMLElement
from wdom.tag import Html, Head, Body, Meta, Link, Title, Script
from wdom.window import Window


def getElementById(id:Union[str, int]) -> Optional[Node]:
    elm = Element._elements_with_id.get(str(id))
    if elm and elm.ownerDocument:
        return elm
    else:
        return None


def getElementByRimoId(id:Union[str, int]) -> Optional[WebElement]:
    elm = WebElement._elements_with_rimo_id.get(str(id))
    if elm and elm.ownerDocument:
        return elm
    else:
        return None


class Document(Node):
    nodeType = Node.DOCUMENT_NODE
    nodeName = '#document'

    @property
    def defaultView(self) -> Window:
        return self._window

    @property
    def connections(self) -> list:
        return self.defaultView.connections

    @property
    def tempdir(self) -> str:
        return self._tempdir_name

    def __init__(self, doctype='html', title='W-DOM', charset='utf-8',
                 default_class=HTMLElement, autoreload=None, reload_wait=None):
        self._tempdir = tempfile.TemporaryDirectory()
        self._tempdir_name = self._tempdir.name
        super().__init__()
        self._window = Window(self)
        self._default_class = default_class
        self._reload_wait = reload_wait
        self.doctype = DocumentType(doctype)
        self.appendChild(self.doctype)

        self.html = Html(parent=self)

        self.head = Head(parent=self.html)
        self.charset_element = Meta(parent=self.head)
        self.characterSet = charset
        self.title_element = Title(parent=self.head)
        self.title = title

        self.body = Body(parent=self.html)
        self.script = Script(parent=self.body)
        self._set_autoreload(autoreload, reload_wait)

    def _set_autoreload(self, autoreload, reload_wait:int=None):
        if autoreload is None:
            self._autoreload = (config.autoreload or config.debug)
        else:
            self._autoreload = autoreload

        if self._autoreload:
            ar_script = []
            ar_script.append('var RIMO_AUTORELOAD = true')
            if reload_wait is not None:
                ar_script.append('var RIMO_RELOAD_WAIT = {}'.format(
                    reload_wait))
            _s = Script(parent=self.head)
            _s.textContent = '\n{}\n'.format('\n'.join(ar_script))

    def getElementById(self, id:Union[str, int]) -> Optional[Node]:
        elm = getElementById(id)
        if elm and elm.ownerDocument is self:
            return elm

    def getElementByRimoId(self, id:Union[str, int]) -> Optional[WebElement]:
        elm = getElementByRimoId(id)
        if elm and elm.ownerDocument is self:
            return elm

    def createElement(self, tag:str):
        return _create_element(tag, base=self._default_class)

    def createDocumentFragment(self):
        return DocumentFragment()

    def createTextNode(self, text:str):
        return Text(text)

    def createComment(self, text:str):
        return Comment(text)

    def createEvent(self, event:str):
        return Event(event)

    def createAttribute(self, name:str):
        return Attr(name)

    @property
    def title(self) -> str:
        return self.title_element.textContent

    @title.setter
    def title(self, value:str):
        self.title_element.textContent = value

    @property
    def characterSet(self) -> str:
        return self.charset_element.getAttribute('charset')

    @characterSet.setter
    def characterSet(self, value:str):
        self.charset_element.setAttribute('charset', value)

    @property
    def charset(self) -> str:
        return self.characterSet

    @charset.setter
    def charset(self, value:str):
        self.characterSet = value

    def add_jsfile(self, src:str):
        self.body.appendChild(Script(src=src))

    def add_jsfile_head(self, src:str):
        self.head.appendChild(Script(src=src))

    def add_cssfile(self, src:str):
        self.head.appendChild(Link(rel='stylesheet', href=src))

    def add_header(self, header:str):
        self.head.appendChild(RawHtml(header))

    def register_theme(self, theme:ModuleType) -> None:
        if not hasattr(theme, 'css_files'):
            raise ValueError('theme module must include `css_files`.')
        for css in getattr(theme, 'css_files', []):
            self.add_cssfile(css)
        for js in getattr(theme, 'js_files', []):
            self.add_jsfile(js)
        for header in getattr(theme, 'headers', []):
            self.add_header(header)
        for cls in getattr(theme, 'extended_classes', []):
            self.defaultView.customElements.define(cls)

    def build(self) -> str:
        return ''.join(child.html for child in self.childNodes)


def get_document(include_rimo: bool = True,
                 include_skeleton: bool = False,
                 include_normalizecss: bool = False,
                 app: Optional[Node] = None,
                 autoreload: Optional[bool] = None,
                 reload_wait: int = None,
                 log_level: int = None,
                 log_prefix: str = None,
                 log_console: bool = False,
                 ws_url: str = None,
                 ) -> Document:
    document = Document(autoreload=autoreload, reload_wait=reload_wait)
    if app:
        document.body.insertBefore(app, document.body.firstChild)
    if log_level is None:
        log_level = config.logging

    log_script = []
    if log_level is not None:
        if isinstance(log_level, str):
            log_script.append('var RIMO_LOG_LEVEL = \'{}\''.format(log_level))
        elif isinstance(log_level, int):
            log_script.append('var RIMO_LOG_LEVEL = {}'.format(log_level))
    if log_prefix is not None:
        log_script.append('var RIMO_LOG_PREFIX = \'{}\''.format(log_prefix))
    if log_console:
        log_script.append('var RIMO_LOG_CONSOLE = true')
    if log_script:
        _s = Script(parent=document.head)
        _s.textContent = '\n{}\n'.format('\n'.join(log_script))

    if ws_url is not None:
        _s = Script(parent=document.head)
        _s.textContent = '\nvar RIMO_WS_URL = \'{}\'\n'.format(ws_url)

    if include_rimo:
        document.add_jsfile_head('_static/js/rimo/rimo.js')

    return document
