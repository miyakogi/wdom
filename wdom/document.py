#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Document class and its helper functions.

This module also provides a deafult root-document object.
"""

import os
import tempfile
import shutil
from functools import partial
from types import ModuleType
from typing import Any, Callable, Optional, Union
import weakref

from wdom import server
from wdom.element import Element, Attr, HTMLElement, getElementsBy
from wdom.element import getElementsByClassName, getElementsByTagName
from wdom.element import querySelector, querySelectorAll
from wdom.event import Event, EventTarget, WebEventTarget
from wdom.node import Node, DocumentType, Text, RawHtml, Comment, ParentNode
from wdom.node import DocumentFragment, NodeList
from wdom.options import config
from wdom.tag import Tag
from wdom.tag import Html, Head, Body, Meta, Link, Title, Script
from wdom.web_node import WdomElement
from wdom.window import Window


def getElementById(id: str) -> Optional[Node]:
    """Get element with ``id``."""
    elm = Element._elements_with_id.get(id)
    return elm


def getElementByWdomId(id: str) -> Optional[WebEventTarget]:
    """Get element with ``wdom_id``."""
    if not id:
        return None
    elif id == 'document':
        return get_document()
    elif id == 'window':
        return get_document().defaultView
    elm = WdomElement._elements_with_wdom_id.get(id)
    return elm


def _cleanup(path: str) -> None:
    """Cleanup temporary directory."""
    if os.path.isdir(path):
        shutil.rmtree(path)


def create_element(tag: str, name: str = None, base: type = None,
                   attr: dict = None) -> Node:
    """Create element with a tag of ``name``.

    :arg str name: html tag.
    :arg type base: Base class of the created element
                       (defatlt: ``WdomElement``)
    :arg dict attr: Attributes (key-value pairs dict) of the new element.
    """
    from wdom.web_node import WdomElement
    from wdom.tag import Tag
    from wdom.window import customElements
    if attr is None:
        attr = {}
    if name:
        base_class = customElements.get((name, tag))
    else:
        base_class = customElements.get((tag, None))
    if base_class is None:
        attr['_registered'] = False
        base_class = base or WdomElement
    if issubclass(base_class, Tag):
        return base_class(**attr)
    return base_class(tag, **attr)


def _find_tag(elm: Node, tag: str) -> Optional[Node]:
    _tag = tag.lower()
    for child in elm.childNodes:
        if child.nodeType == Element.nodeType and child.localName == _tag:
            return child
    return None


class Document(Node, ParentNode, EventTarget):
    """Base class for Document node."""

    nodeType = Node.DOCUMENT_NODE
    nodeName = '#document'

    def __init__(self, *,
                 doctype: str = 'html',
                 default_class: type = HTMLElement,
                 **kwargs: Any) -> None:
        """Create new Document node.

        :arg str doctype: Document type of this document.
        :arg type default_class: Default class created by
            :py:meth:`createElement` method.
        """
        super().__init__()
        self.__window = Window(self)
        self._default_class = default_class

        self.__doctype = DocumentType(doctype, parent=self)
        self.__html = Html(parent=self)
        self.__head = Head(parent=self.documentElement)
        self.__body = Body(parent=self.documentElement)

    @property
    def defaultView(self) -> Window:
        """Return :class:`Window` class of this document."""
        return self.__window

    @property
    def doctype(self) -> DocumentType:
        """Return DocumentType element of this document."""
        return self.__doctype

    @property
    def documentElement(self) -> Element:
        """Return <html> element of this document."""
        return self.__html

    @property
    def head(self) -> Element:
        """Return <head> element of this document."""
        return self.__head

    def _find_charset_node(self) -> Optional[Element]:
        for child in self.head:
            if child.localName == 'meta' and child.hasAttribute('charset'):
                return child
        return None

    @property
    def characterSet(self) -> str:
        """Get/Set charset of this document."""
        charset = self._find_charset_node()
        if charset:
            return charset.getAttribute('charset')  # type: ignore
        return ''

    @characterSet.setter
    def characterSet(self, charset: str) -> None:
        """Set character set of this document."""
        charset_node = self._find_charset_node() or Meta(parent=self.head)
        charset_node.setAttribute('charset', charset)

    @property
    def body(self) -> Element:
        """Return <body> element of this document."""
        return self.__body

    @property
    def title(self) -> str:
        """Get/Set title string of this document."""
        title_element = _find_tag(self.head, 'title')
        if title_element:
            return title_element.textContent
        return ''

    @title.setter
    def title(self, new_title: str) -> None:
        _title = _find_tag(self.head, 'title')
        title_element = _title or Title(parent=self.head)
        title_element.textContent = new_title

    def getElementsBy(self, cond: Callable[[Element], bool]) -> NodeList:
        """Get elements in this document which matches condition."""
        return getElementsBy(self, cond)

    def getElementsByTagName(self, tag: str) -> NodeList:
        """Get elements with tag name in this document."""
        return getElementsByTagName(self, tag)

    def getElementsByClassName(self, class_name: str) -> NodeList:
        """Get elements with class name in this document."""
        return getElementsByClassName(self, class_name)

    def getElementById(self, id: str) -> Optional[Node]:
        """Get element by ``id``.

        If this document does not have the element with the id, return None.
        """
        elm = getElementById(id)
        if elm and elm.ownerDocument is self:
            return elm
        return None

    def createDocumentFragment(self) -> DocumentFragment:
        """Create empty document fragment."""
        return DocumentFragment()

    def createTextNode(self, text: str) -> Text:
        """Create text node with ``text``."""
        return Text(text)

    def createComment(self, comment: str) -> Comment:
        """Create comment node with ``comment``."""
        return Comment(comment)

    def createElement(self, tag: str) -> Node:
        """Create new element whose tag name is ``tag``."""
        return create_element(tag, base=self._default_class)

    def createEvent(self, event: str) -> Event:
        """Create Event object with ``event`` type."""
        return Event(event)

    def createAttribute(self, name: str) -> Attr:
        """Create Attribute object with ``name``."""
        return Attr(name)

    def querySelector(self, selectors: str) -> Node:
        """Not Implemented."""
        return querySelector(self, selectors)

    def querySelectorAll(self, selectors: str) -> NodeList:
        """Not Implemented."""
        return querySelectorAll(self, selectors)


class WdomDocument(Document, WebEventTarget):
    """Main document class for WDOM applications."""

    @property
    def wdom_id(self) -> str:  # noqa: D102
        return 'document'

    @property
    def connected(self) -> bool:  # noqa: D102
        return server.is_connected()

    @property
    def tempdir(self) -> str:
        """Return temporary directory used by this document."""
        return self.__tempdir

    def __init__(self, *,
                 doctype: str = 'html',
                 title: str = 'W-DOM',
                 charset: str = 'utf-8',
                 default_class: type = WdomElement,
                 autoreload: bool = None,
                 reload_wait: float =None,
                 **kwargs: Any) -> None:
        """Create new document object for WDOM application.

        .. caution::

            Don't create new document from :class:`WdomDocument` class
            constructor. Use :func:`get_new_document` function instead.

        :arg str doctype: doctype of the document (default: html).
        :arg str title: title of the document.
        :arg str charset: charset of the document.
        :arg type default_class: Set default Node class of the document. This
            class is used when make node by :py:meth:`createElement()`
        :arg bool autoreload: Enable/Disable autoreload (default: False).
        :arg float reload_wait: How long (seconds) wait to reload. This
            parameter is only used when autoreload is enabled.
        """
        self.__tempdir = _tempdir = tempfile.mkdtemp()
        self._finalizer = weakref.finalize(self,  # type: ignore
                                           partial(_cleanup, _tempdir))
        self._autoreload = autoreload
        self._reload_wait = reload_wait

        super().__init__(doctype=doctype, default_class=default_class)
        self.characterSet = charset
        self.title = title
        self.script = Script(parent=self.body)
        self._autoreload_script = Script(parent=self.head)
        self.addEventListener('mount', self._on_mount)

    def _set_autoreload(self) -> None:
        self._autoreload_script.textContent = ''
        if self._autoreload is None:
            autoreload = (config.autoreload or config.debug)
        else:
            autoreload = self._autoreload

        if autoreload:
            ar_script = []
            ar_script.append('var WDOM_AUTORELOAD = true')
            if self._reload_wait is not None:
                ar_script.append('var WDOM_RELOAD_WAIT = {}'.format(
                    self._reload_wait))
            self._autoreload_script.textContent = '\n{}\n'.format(
                '\n'.join(ar_script))

    def getElementByWdomId(self, id: Union[str]) -> Optional[WebEventTarget]:
        """Get an element node with ``wdom_id``.

        If this document does not have the element with the id, return None.
        """
        elm = getElementByWdomId(id)
        if elm and elm.ownerDocument is self:
            return elm
        return None

    def add_jsfile(self, src: str) -> None:
        """Add JS file to load at this document's bottom of the body."""
        self.body.appendChild(Script(src=src))

    def add_jsfile_head(self, src: str) -> None:
        """Add JS file to load at this document's header."""
        self.head.appendChild(Script(src=src))

    def add_cssfile(self, src: str) -> None:
        """Add CSS file to load at this document's header."""
        self.head.appendChild(Link(rel='stylesheet', href=src))

    def add_header(self, header: str) -> None:
        """Insert header tag staring at this document's header.

        :arg str header: tag to insert <head> ~ </head> area.
        """
        self.head.appendChild(RawHtml(header))

    def register_theme(self, theme: ModuleType) -> None:
        """Set theme for this docuemnt.

        This method sets theme's js/css files and headers on this document.

        :arg ModuleType theme: a module which has ``js_files``, ``css_files``,
            ``headers``, and ``extended_classes``. see ``wdom.themes``
            directory actual theme module structures.
        """
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
        """Return HTML representation of this document."""
        self._set_autoreload()
        return ''.join(child.html for child in self.childNodes)


def get_new_document(  # noqa: C901
        include_wdom_js: bool = True,
        include_skeleton: bool = False,
        include_normalizecss: bool = False,
        autoreload: bool = None,
        reload_wait: float = None,
        log_level: Union[int, str] = None,
        log_prefix: str = None,
        log_console: bool = False,
        ws_url: str = None,
        message_wait: float = None,
        document_factory: Callable[..., Document] = WdomDocument,
        **kwargs: Any) -> Document:
    """Create new :class:`Document` object with options.

    :arg bool include_wdom_js: Include wdom.js file. Usually should be True.
    :arg bool include_skeleton: Include skelton.css.
    :arg bool include_normalizecss: Include normalize.css.
    :arg bool autoreload: Enable autoreload flag. This flag overwrites
        ``--debug`` flag, which automatically enables autoreload.
    :arg float reload_wait: Seconds to wait until reload when autoreload is
        enabled.
    :arg str log_level: Log level string, chosen from DEBUG, INFO, WARN, ERROR.
        Integer values are also acceptable like ``logging.INFO``. By default
        use ``wdom.config.options.log_level``, which default is ``INFO``.
    :arg str log_prefix: Prefix of log outputs.
    :arg bool log_console: Flag to show wdom log on browser console.
    :arg str ws_url: URL string to the ws url.
        Default: ``ws://localhost:8888/wdom_ws``.
    :arg float message_wait: Duration (seconds) to send WS messages.
    :arg Callable document_factory: Factory function/class to create Document
        object.
    :rtype: Document
    """
    document = document_factory(
        autoreload=autoreload,
        reload_wait=reload_wait,
        **kwargs
    )

    if log_level is None:
        log_level = config.logging
    if message_wait is None:
        message_wait = config.message_wait

    log_script = []
    log_script.append('var WDOM_MESSAGE_WAIT = {}'.format(message_wait))
    if isinstance(log_level, str):
        log_script.append('var WDOM_LOG_LEVEL = \'{}\''.format(log_level))
    elif isinstance(log_level, int):
        log_script.append('var WDOM_LOG_LEVEL = {}'.format(log_level))
    if log_prefix:
        log_script.append('var WDOM_LOG_PREFIX = \'{}\''.format(log_prefix))
    if log_console:
        log_script.append('var WDOM_LOG_CONSOLE = true')
    if log_script:
        _s = Script(parent=document.head)
        _s.textContent = '\n{}\n'.format('\n'.join(log_script))

    if ws_url:
        _s = Script(parent=document.head)
        _s.textContent = '\nvar WDOM_WS_URL = \'{}\'\n'.format(ws_url)

    if include_wdom_js:
        document.add_jsfile_head('_static/js/wdom.js')

    return document


def get_document() -> Document:
    """Get current root document object.

    :rtype: Document
    """
    return rootDocument


def set_document(new_document: Document) -> None:
    """Set a new document as a current root document.

    :param Document new_document: New root document.
    """
    global rootDocument
    rootDocument = new_document


def set_app(app: Tag) -> None:
    """Set ``Tag`` as applicaion to the current root document.

    Equivalent to ``get_document().body.prepend(app)``.
    """
    document = get_document()
    document.body.prepend(app)


rootDocument = get_new_document()
