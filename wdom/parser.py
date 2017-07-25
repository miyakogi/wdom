#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import HTML_EMPTY  # type: ignore
from html.parser import HTMLParser
from typing import Any, List, Tuple, TYPE_CHECKING

from wdom.node import Node  # noqa

if TYPE_CHECKING:
    from typing import Optional  # noqa


class FragmentParser(HTMLParser):
    default_class = None  # type: Optional[type]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore
        from wdom.node import DocumentFragment
        self.elm = DocumentFragment()  # type: Node
        self.root = self.elm

    def handle_starttag(self, tag: str, attr: List[Tuple[str, str]]) -> None:
        from wdom.document import create_element
        attrs = dict(attr)
        params = dict(parent=self.elm, **attrs)
        elm = create_element(tag, attrs.get('is'), self.default_class, params)
        if self.elm:
            self.elm.append(elm)
        if tag not in HTML_EMPTY:
            self.elm = elm

    def handle_endtag(self, tag: str) -> None:
        self.elm = self.elm.parentNode  # type: ignore

    def handle_data(self, data: str) -> None:
        if data and self.elm:
            self.elm.append(data)

    def handle_comment(self, comment: str) -> None:
        from wdom.node import Comment
        self.elm.append(Comment(comment))


class DocumentParser(FragmentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        from wdom.document import Document
        self.root = Document()
        self.elm = self.root.body  # type: ignore

    def handle_decl(self, decl: str) -> None:
        if decl.startswith('DOCTYPE'):
            self.root.doctype.name = decl.split()[-1]

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        if tag == 'html':
            # mypy ignores asignment in Document.__init__()
            self.elm = self.root.html  # type: ignore
        elif tag == 'head':
            self.elm = self.root.head
        elif tag == 'body':
            self.elm = self.root.body
        else:
            super().handle_starttag(tag, attrs)


def parse_document(doc: str) -> Node:
    parser = DocumentParser()
    parser.feed(doc)
    return parser.root


def parse_html(html: str) -> Node:
    parser = FragmentParser()
    parser.feed(html)
    return parser.root
