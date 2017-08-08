#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Web-connected HTML tag classes."""

import logging
from collections import Iterable
from typing import Any, Dict, Union, TYPE_CHECKING
from types import new_class

from wdom.element import _AttrValueType
from wdom.element import (
    HTMLAnchorElement,
    HTMLButtonElement,
    HTMLFormElement,
    HTMLIFrameElement,
    HTMLInputElement,
    HTMLLabelElement,
    HTMLOptGroupElement,
    HTMLOptionElement,
    HTMLScriptElement,
    HTMLSelectElement,
    HTMLStyleElement,
    HTMLTextAreaElement,
)
from wdom.node import Node, NodeList
# Just export Comment/RawHtml/Text
from wdom.node import Comment, RawHtml, Text  # noqa: F401
from wdom.web_node import WdomElement

if TYPE_CHECKING:
    from typing import List, Type  # noqa

logger = logging.getLogger(__name__)


class Tag(WdomElement):
    """Base class for html tags.

    ``HTMLElement`` requires to specify tag name when instanciate it, but this
    class and sublasses have default tag name and not need to specify it for
    each thier instances.
    """

    #: Tag name used for this node.
    tag = 'tag'
    #: use for <input> tag's type
    type_ = ''
    #: custom element which extends built-in tag (like <table is="your-tag">)
    is_ = ''

    def __init__(self, *args: Any, attrs: Dict[str, _AttrValueType] = None,
                 **kwargs: Any) -> None:  # noqa: D102
        if attrs:
            kwargs.update(attrs)
        if self.type_ and 'type' not in kwargs:
            kwargs['type'] = self.type_
        if self.is_ and 'is' not in kwargs and 'is_' not in kwargs:
            kwargs['is'] = self.is_
        super().__init__(self.tag, **kwargs)  # type: ignore
        self.append(*args)

    def _clone_node(self) -> 'Tag':
        """Need to copy class, not tag.

        So need to re-implement copy.
        """
        clone = type(self)()
        for attr in self.attributes:
            clone.setAttribute(attr, self.getAttribute(attr))
        for c in self.classList:
            clone.addClass(c)
        clone.style.update(self.style)
        # TODO: should clone event listeners???
        return clone

    __copy__ = _clone_node  # need alias again

    @property
    def type(self) -> _AttrValueType:  # noqa: D102
        return self.getAttribute('type') or self.type_

    @type.setter
    def type(self, val: str) -> None:  # noqa: D102
        self.setAttribute('type', val)


class NestedTag(Tag):
    """NestedTag class.

    Useful to make component made by nested, multiple tags.
    """

    #: Inner nested tag class
    inner_tag_class = None  # type: Type[Node]

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        self._inner_element = None
        super().__init__(**kwargs)
        if self.inner_tag_class:
            self._inner_element = self.inner_tag_class()
            super().appendChild(self._inner_element)
        self.append(*args)

    def appendChild(self, child: Node) -> Node:  # noqa: D102
        if self._inner_element:
            return self._inner_element.appendChild(child)
        return super().appendChild(child)

    def insertBefore(self, child: Node, ref_node: Node) -> Node:  # noqa: D102
        if self._inner_element:
            return self._inner_element.insertBefore(child, ref_node)
        return super().insertBefore(child, ref_node)

    def removeChild(self, child: Node) -> Node:  # noqa: D102
        if self._inner_element:
            return self._inner_element.removeChild(child)
        return super().removeChild(child)

    def replaceChild(self, new_child: Node, old_child: Node
                     ) -> Node:  # noqa: D102
        if self._inner_element:
            return self._inner_element.replaceChild(new_child, old_child)
        return super().replaceChild(new_child, old_child)

    @property
    def childNodes(self) -> NodeList:  # noqa: D102
        if self._inner_element:
            return self._inner_element.childNodes
        return super().childNodes

    def empty(self) -> None:  # noqa: D102
        if self._inner_element:
            self._inner_element.empty()
        else:
            super().empty()

    @Tag.textContent.setter
    def textContent(self, text: str) -> None:  # type: ignore
        """Set text content to inner node."""
        if self._inner_element:
            self._inner_element.textContent = text
        else:
            # Need a trick to call property of super-class
            super().textContent = text  # type: ignore

    @property
    def html(self) -> str:
        """Get whole html representation of this node."""
        if self._inner_element:
            return self.start_tag + self._inner_element.html + self.end_tag
        return super().html

    @property
    def innerHTML(self) -> str:
        """Get innerHTML of the inner node."""
        if self._inner_element:
            return self._inner_element.innerHTML
        return super().innerHTML

    @innerHTML.setter
    def innerHTML(self, html: str) -> None:
        """Set html to inner node."""
        if self._inner_element:
            self._inner_element.innerHTML = html
        else:
            super().innerHTML = html  # type: ignore


def NewTagClass(class_name: str, tag: str = None,
                bases: Union[type, Iterable] = (Tag, ),
                **kwargs: Any) -> type:
    """Generate and return new ``Tag`` class.

    If ``tag`` is empty, lower case of ``class_name`` is used for a tag name of
    the new class. ``bases`` should be a tuple of base classes. If it is empty,
    use ``Tag`` class for a base class. Other keyword arguments are used for
    class variables of the new class.

    Example::

        MyButton = NewTagClass('MyButton', 'button', (Button,),
                               class_='btn', is_='my-button')
        my_button = MyButton('Click!')
        print(my_button.html)

        >>> <button class="btn" id="111111111" is="my-button">Click!</button>
    """
    if tag is None:
        tag = class_name.lower()
    if not isinstance(type, tuple):
        if isinstance(bases, Iterable):
            bases = tuple(bases)
        elif isinstance(bases, type):
            bases = (bases, )
        else:
            TypeError('Invalid base class: {}'.format(str(bases)))
    kwargs['tag'] = tag
    # Here not use type() function, since it does not support
    # metaclasss (__prepare__) properly.
    cls = new_class(  # type: ignore
        class_name, bases, {}, lambda ns: ns.update(kwargs))
    return cls


class Input(Tag, HTMLInputElement):
    """Base class for ``<input>`` element."""

    tag = 'input'
    #: type attribute; text, button, checkbox, or radio... and so on.
    type_ = ''

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        if self.type_ and 'type' not in kwargs:
            kwargs['type'] = self.type_
        super().__init__(*args, **kwargs)


class Textarea(Tag, HTMLTextAreaElement):  # noqa: D204
    """Base class for ``<textarea>`` element."""
    tag = 'textarea'

    @property
    def value(self) -> str:
        """Get input value of this node.

        This value is used as a default value of this element.
        """
        return self.textContent

    @value.setter
    def value(self, value: str) -> None:
        self.textContent = value


class Script(Tag, HTMLScriptElement):  # noqa: D204
    """Base class for <script> tag.

    Inner contents of this node is not escaped.
    """
    tag = 'script'

    def __init__(self, *args: Any, type: str = 'text/javascript',
                 **kwargs: Any) -> None:  # noqa: D102
        super().__init__(*args, type=type, **kwargs)


Html = NewTagClass('Html')
Body = NewTagClass('Body')
Meta = NewTagClass('Meta')
Head = NewTagClass('Head')
Link = NewTagClass('Link')
Title = NewTagClass('Title')
Style = NewTagClass('Style', 'style', (Tag, HTMLStyleElement))
Iframe = NewTagClass('Iframe', 'iframe', (Tag, HTMLIFrameElement))

Div = NewTagClass('Div')
Span = NewTagClass('Span')

# Typography
H1 = NewTagClass('H1')
H2 = NewTagClass('H2')
H3 = NewTagClass('H3')
H4 = NewTagClass('H4')
H5 = NewTagClass('H5')
H6 = NewTagClass('H6')

P = NewTagClass('P')
A = NewTagClass('A', 'a', (Tag, HTMLAnchorElement))
Strong = NewTagClass('Strong')
Em = NewTagClass('Em')
U = NewTagClass('U')
Br = NewTagClass('Br')
Hr = NewTagClass('Hr')

Cite = NewTagClass('Cite')
Code = NewTagClass('Code')
Pre = NewTagClass('Pre')

Img = NewTagClass('Img')

# table tags
Table = NewTagClass('Table')
Thead = NewTagClass('Thead')
Tbody = NewTagClass('Tbody')
Tfoot = NewTagClass('Tfoot')
Th = NewTagClass('Th')
Tr = NewTagClass('Tr')
Td = NewTagClass('Td')

# List tags
Ol = NewTagClass('Ol')
Ul = NewTagClass('Ul')
Li = NewTagClass('Li')

# Definition-list tags
Dl = NewTagClass('Dl')
Dt = NewTagClass('Dt')
Dd = NewTagClass('Dd')

# Form controls
Form = NewTagClass('Form', 'form', (Tag, HTMLFormElement))
Button = NewTagClass('Button', 'button', (Tag, HTMLButtonElement))
Label = NewTagClass('Label', 'label', (Tag, HTMLLabelElement))
Optgroup = NewTagClass('Optgroup', 'optgroup', (Tag, HTMLOptGroupElement))
Option = NewTagClass('Option', 'option', (Tag, HTMLOptionElement))
Select = NewTagClass('Select', 'select', (Tag, HTMLSelectElement))


class RawHtmlNode(Tag):
    """Does not escape inner contents, similar to ``<script>`` tag.

    This node wraps contents by ``<div style="display: inline">...</div>`` and
    does not escape inner text. Similar to ``wdom.node.RawHtmlNode``, but the
    difference is this class wraps text by div tag. This enables to treat
    multi-tag html string as if it's single node.

    Useful for showing generated HTML contents, like markdown conversion
    result, graph plots, or HTML formatted reports.
    Usually faster than ``Tag.innerHTML = html``, since this node skips html
    parsing process to WdomElement.

    Example::

        doc.body.appnd(RawHtml('<h1>Title</h1>'))

    .. note::

        Inner html is not WdomElement, so you cant control them from python.
    """

    tag = 'div'
    _should_escape_text = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Add ``display: inline`` style on div tag."""
        super().__init__(*args, **kwargs)
        if 'display' not in self.style:
            self.style.setProperty('display', 'inline')


default_classes = (
    Input,
    Textarea,
    Script,
    Html,
    Body,
    Meta,
    Head,
    Link,
    Title,
    Style,
    Div,
    Span,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
    P,
    A,
    Strong,
    Em,
    U,
    Br,
    Hr,
    Cite,
    Code,
    Pre,
    Img,
    Table,
    Thead,
    Tbody,
    Tfoot,
    Th,
    Tr,
    Td,
    Ol,
    Ul,
    Li,
    Dl,
    Dt,
    Dd,
    Form,
    Button,
    Label,
    Optgroup,
    Option,
    Select,
)

# alias
OptGroup = Optgroup
TextArea = Textarea
