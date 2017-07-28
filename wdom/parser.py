#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parser base classes to parse HTML to Wdom objects."""

from xml.etree.ElementTree import HTML_EMPTY  # type: ignore
from html.parser import HTMLParser
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

from wdom.node import Node, Text, RawHtml

if TYPE_CHECKING:
    from wdom.document import Document  # noqa

_NOESCAPE = ['script', 'style']


class FragmentParser(HTMLParser):
    """Parser class to parse HTML fragment strings.

    Node class to be generated from parse result is defined by
    ``default_class`` class attribute.
    """

    default_class = None  # type: Optional[type]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize parser."""
        super().__init__(*args, **kwargs)  # type: ignore
        from wdom.node import DocumentFragment
        self.elm = DocumentFragment()  # type: Node
        self.root = self.elm
        self.current_tag = ''

    def handle_starttag(self, tag: str, attr: List[Tuple[str, str]]
                        ) -> None:  # noqa: D102
        from wdom.document import create_element
        self.current_tag = tag
        attrs = dict(attr)
        params = dict(parent=self.elm, **attrs)
        elm = create_element(tag, attrs.get('is'), self.default_class, params)
        if self.elm:
            self.elm.appendChild(elm)
        if tag not in HTML_EMPTY:
            self.elm = elm

    def handle_endtag(self, tag: str) -> None:  # noqa: D102
        parent = self.elm.parentNode
        if parent is None:
            if self.elm is not self.root:
                raise ValueError('Parse Failed')
        else:
            self.elm = parent

    def handle_data(self, data: str) -> None:  # noqa: D102
        if data:
            if self.current_tag in _NOESCAPE:
                self.elm.appendChild(RawHtml(data))
            else:
                self.elm.appendChild(Text(data))

    def handle_comment(self, comment: str) -> None:  # noqa: D102
        from wdom.node import Comment
        self.elm.appendChild(Comment(comment))


class DocumentParser(FragmentParser):
    """Parser class to parse whole HTML document."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        super().__init__(*args, **kwargs)
        from wdom.document import Document  # noqa
        doc = Document()
        self.root = doc  # type: Document
        self.elm = doc.body  # type: Node

    def handle_decl(self, decl: str) -> None:  # noqa: D102
        if decl.startswith('DOCTYPE'):
            self.root.doctype.name = decl.split()[-1]

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]
                        ) -> None:  # noqa: D102
        if tag == 'html':
            # mypy ignores asignment in Document.__init__()
            doc = self.root  # type: Document
            self.elm = doc.html  # type: Node
        elif tag == 'head':
            self.elm = self.root.head
        elif tag == 'body':
            self.elm = self.root.body
        else:
            super().handle_starttag(tag, attrs)


def parse_document(doc: str) -> 'Document':
    """Parse HTML document and return Document object."""
    parser = DocumentParser()
    parser.feed(doc)
    return parser.root


def parse_html(html: str, parser: Optional[FragmentParser] = None) -> Node:
    """Parse HTML fragment and return DocumentFragment object.

    DocumentFragment object has parsed Node objects as its child nodes.
    """
    parser = parser or FragmentParser()
    parser.feed(html)
    return parser.root
