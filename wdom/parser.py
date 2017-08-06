#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parser base classes to parse HTML to Wdom objects."""

from xml.etree.ElementTree import HTML_EMPTY  # type: ignore
from html.parser import HTMLParser
from typing import Any, Callable, List, Optional, Tuple, TYPE_CHECKING

from wdom.node import Node, Text, RawHtml

if TYPE_CHECKING:
    from wdom.document import Document  # noqa

_NOESCAPE = ['script', 'style']
_T_ElementFactory = Callable[[str, Optional[str], Optional[type], dict], Node]


class FragmentParser(HTMLParser):
    """Parser class to parse HTML fragment strings.

    If unknown tag is found, ``default_class`` is used to generate noew.
    """

    #: Class of unknown tag
    default_class = None  # type: Optional[type]

    def __init__(self, *args: Any,
                 element_factory:  _T_ElementFactory = None,
                 **kwargs: Any) -> None:
        """Initialize parser."""
        super().__init__(*args, **kwargs)  # type: ignore
        from wdom.node import DocumentFragment
        from wdom.document import create_element
        self.elm = DocumentFragment()  # type: Node
        self.root = self.elm
        self.current_tag = ''
        self.element_factory = element_factory or create_element

    def handle_starttag(self, tag: str, attr: List[Tuple[str, str]]
                        ) -> None:  # noqa: D102
        self.current_tag = tag
        attrs = dict(attr)
        params = dict(parent=self.elm, **attrs)
        elm = self.element_factory(
            tag, attrs.get('is'), self.default_class, params)
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


def parse_html(html: str, parser: Optional[FragmentParser] = None) -> Node:
    """Parse HTML fragment and return DocumentFragment object.

    DocumentFragment object has parsed Node objects as its child nodes.
    """
    parser = parser or FragmentParser()
    parser.feed(html)
    return parser.root


if __name__ == '__main__':
    from cProfile import Profile
    from pstats import Stats
    from functools import partial
    from pathlib import Path
    root = Path(__file__).absolute().parent.parent
    html_file = root / 'DOM_Standard.html'
    with open(html_file) as f:
        src = f.read()
    test = partial(parse_html, src)
    profiler = Profile()
    profiler.runcall(test)  # type: ignore
    stats = Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats()
