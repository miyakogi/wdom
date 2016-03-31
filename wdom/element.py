#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Iterable, OrderedDict
from functools import partial
from xml.etree.ElementTree import HTML_EMPTY
from html.parser import HTMLParser
from typing import Union, Tuple
from weakref import WeakSet, WeakValueDictionary

from wdom.interface import NodeList
from wdom.css import CSSStyleDeclaration
from wdom.node import Node, ParentNode, ChildNode, DocumentFragment, Comment
from wdom.event import EventTarget
from wdom.webif import WebIF


class DOMTokenList:
    def __init__(self, owner, *args):
        self._list = list()
        self._owner = owner
        self._append(args)

    def __len__(self) -> int:
        return len(self._list)

    def __contains__(self, item:str) -> bool:
        return item in self._list

    def __iter__(self) -> str:
        for token in self._list:
            yield token

    def _validate_token(self, token:str):
        if not isinstance(token, str):
            raise TypeError(
                'Token must be str, but {} passed.'.format(type(token)))
        if ' ' in token:
            raise ValueError(
                'Token contains space characters, which are invalid.')

    def _append(self, token):
        if isinstance(token, str):
            for t in token.split(' '):
                self.add(t)
        elif isinstance(token, Iterable):
            for t in token:
                self._append(t)
        elif token is None:
            pass
        else:
            raise TypeError

    @property
    def length(self) -> int:
        return len(self)

    def add(self, *tokens:Tuple[str]):
        _new_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token and token not in self:
                self._list.append(token)
                _new_tokens.append(token)
        if isinstance(self._owner, WebIF) and _new_tokens:
            self._owner.js_exec('addClass', classes=_new_tokens)

    def remove(self, *tokens:Tuple[str]):
        _removed_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token in self:
                self._list.remove(token)
                _removed_tokens.append(token)
        if isinstance(self._owner, WebIF) and _removed_tokens:
            self._owner.js_exec('removeClass', classes=_removed_tokens)

    def toggle(self, token:str):
        self._validate_token(token)
        if token in self:
            self.remove(token)
        else:
            self.add(token)

    def item(self, index:int) -> str:
        if 0 <= index < len(self):
            return self._list[index]
        else:
            return None

    def contains(self, token:str) -> bool:
        self._validate_token(token)
        return token in self

    def toString(self) -> str:
        return ' '.join(self)


class Attr:
    _boolean_attrs = (
        'async', 'autofocus', 'autoplay', 'checked', 'contenteditable',
        'defer', 'disabled', 'draggable', 'dropzone', 'formnovalidate',
        'hidden', 'ismap', 'loop', 'multiple', 'muted', 'novalidate',
        'readonly', 'required', 'reversed', 'spellcheck', 'scoped', 'selected',
    )

    def __init__(self, name:str, value=None, owner: Node = None):
        self._name = name
        self._value = value
        self._owner = owner

    @property
    def html(self) -> str:
        if self.name.lower() in self._boolean_attrs:
            return self.name if self.value else ''
        else:
            return '{name}="{value}"'.format(name=self.name, value=self.value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def isId(self) -> bool:
        return self.name.lower() == 'id'


class NamedNodeMap:
    def __init__(self, owner):
        self._owner = owner
        self._dict = OrderedDict()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, item:str) -> bool:
        return item in self._dict

    def __getitem__(self, index: Union[int, str]) -> Attr:
        if isinstance(index, int):
            return tuple(self._dict.values())[index]
        else:
            return None

    def __iter__(self) -> Attr:
        for attr in self._dict.keys():
            yield attr

    @property
    def length(self) -> int:
        return len(self)

    def getNamedItem(self, name:str) -> Attr:
        return self._dict.get(name, None)

    def setNamedItem(self, item: Attr):
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('setAttribute', attr=item.name,
                                value=item.value)
        self._dict[item.name] = item

    def removeNamedItem(self, item:Attr) -> Attr:
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('removeAttribute', attr=item.name)
        return self._dict.pop(item.name, None)

    def item(self, index:int) -> Attr:
        if 0 <= index < len(self):
            return self._dict[tuple(self._dict.keys())[index]]
        else:
            return None

    def toString(self) -> str:
        return ' '.join(attr.html for attr in self._dict.values())


def _create_element(tag:str, name:str=None, base:type=None, attr:dict=None):
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
        base_class = base or HTMLElement
    if issubclass(base_class, Tag):
        return base_class(**attr)
    else:
        return base_class(tag, **attr)


class Parser(HTMLParser):
    def __init__(self, *args, default_class=None, **kwargs):
        # Import here
        self.default_class = default_class or HTMLElement
        super().__init__(*args, **kwargs)
        self.elm = DocumentFragment()
        self.root = self.elm

    def handle_starttag(self, tag, attr):
        attrs = dict(attr)
        params = dict(parent=self.elm, **attrs)
        elm = _create_element(tag, attrs.get('is'), self.default_class, params)
        if self.elm is not None:
            self.elm.append(elm)
        if tag not in HTML_EMPTY:
            self.elm = elm

    def handle_endtag(self, tag):
        self.elm = self.elm.parentNode

    def handle_data(self, data):
        if data and self.elm is not None:
            self.elm.append(data)

    def handle_comment(self, comment:str):
        self.elm.append(Comment(comment))


class Element(Node, EventTarget, ParentNode, ChildNode):
    nodeType = Node.ELEMENT_NODE
    nodeValue = None
    _parser_default_class = None
    _elements = WeakSet()
    _elements_withid = WeakValueDictionary()

    def __init__(self, tag:str='', parent=None, _registered=True, **kwargs):
        super().__init__(parent=parent)
        self._registered = _registered
        self._elements.add(self)
        self.tag = tag
        self.attributes = NamedNodeMap(self)
        self.classList = DOMTokenList(self)

        if 'class_' in kwargs:
            kwargs['class'] = kwargs.pop('class_')
        if 'is_' in kwargs:
            kwargs['is'] = kwargs.pop('is_')
        for k, v in kwargs.items():
            self.setAttribute(k, v)

    def __copy__(self) -> 'Element':
        clone = type(self)(self.tag)
        for attr in self.attributes:
            clone.setAttribute(attr, self.getAttribute(attr))
        return clone

    def _get_attrs_by_string(self) -> str:
        # attrs = ' '.join(attr.html for attr in self.attributes.values())
        attrs = self.attributes.toString()
        classes = self.getAttribute('class')
        if classes:
            attrs = ' '.join((attrs.strip(), 'class="{}"'.format(classes)))
        return attrs.strip()

    @property
    def start_tag(self) -> str:
        tag = '<' + self.tag
        attrs = self._get_attrs_by_string()
        if attrs:
            tag = ' '.join((tag, attrs))
        return tag + '>'

    def _get_inner_html(self) -> str:
        return ''.join(child.html for child in self._children)

    def _set_inner_html(self, html:str):
        self._empty()
        parser = Parser(default_class=self._parser_default_class)
        parser.feed(html)
        self._append_child(parser.root)

    @property
    def innerHTML(self) -> str:
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html:str):
        self._set_inner_html(html)

    @property
    def end_tag(self) -> str:
        return '</{}>'.format(self.tag)

    @property
    def html(self) -> str:
        return self.start_tag + self.innerHTML + self.end_tag

    @property
    def outerHTML(self) -> str:
        return self.html

    @property
    def nodeName(self) -> str:
        return self.tag.upper()

    @property
    def tagName(self) -> str:
        return self.tag.upper()

    @property
    def localName(self) -> str:
        return self.tag.lower()

    @property
    def id(self) -> str:
        return self.getAttribute('id') or ''

    @id.setter
    def id(self, id:str):
        self.setAttribute('id', id)

    def getAttribute(self, attr:str) -> str:
        if attr == 'class':
            if self.classList:
                return self.classList.toString()
            else:
                return None
        attr_node = self.getAttributeNode(attr)
        if attr_node is None:
            return None
        else:
            return attr_node.value

    def getAttributeNode(self, attr:str) -> Attr:
        return self.attributes.getNamedItem(attr)

    def hasAttribute(self, attr:str) -> bool:
        if attr == 'class':
            return bool(self.classList)
        else:
            return attr in self.attributes

    def hasAttributes(self) -> bool:
        return bool(self.attributes) or bool(self.classList)

    def _set_attribute(self, attr:str, value=None):
        if attr == 'class':
            self.classList = DOMTokenList(self, value)
        else:
            if attr == 'id':
                if 'id' in self.attributes:
                    # remove old reference to self
                    self._elements_withid.pop(self.id, None)
                # register this elements with new id
                self._elements_withid[value] = self
            new_attr_node = Attr(attr, value)
            self.setAttributeNode(new_attr_node)

    def setAttribute(self, attr:str, value=None):
        self._set_attribute(attr, value)

    def setAttributeNode(self, attr:Attr):
        self.attributes.setNamedItem(attr)

    def _remove_attribute(self, attr:str):
        if attr == 'class':
            self.classList = DOMTokenList(self)
        else:
            if attr == 'id':
                self._elements_withid.pop(self.id, None)
            self.attributes.removeNamedItem(Attr(attr))

    def removeAttribute(self, attr:str):
        self._remove_attribute(attr)

    def removeAttributeNode(self, attr:Attr):
        self.attributes.removeNamedItem(attr)

    def getElementsBy(self, cond):
        '''Return list of child nodes which matches ``cond``.
        ``cond`` must be a function which gets a single argument ``node``,
        and returns bool. If the node matches requested condition, ``cond``
        should return True.
        This searches all child nodes recursively.
        '''
        elements = []
        for child in self._children:
            if cond(child):
                elements.append(child)
            if isinstance(child, Element):
                elements.extend(child.getElementsBy(cond))
        return NodeList(elements)

    def getElementsByTagName(self, tag:str):
        _tag = tag.upper()
        cond = lambda node: getattr(node, 'tagName') == _tag
        return self.getElementsBy(cond)

    def getElementsByClassName(self, class_name:str):
        cond = lambda node: class_name in getattr(node, 'classList')
        return self.getElementsBy(cond)


class HTMLElement(Element):
    def __init__(self, *args, style:str=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = CSSStyleDeclaration(style, owner=self)

    def _get_attrs_by_string(self) -> str:
        attrs = super()._get_attrs_by_string()
        style = self.getAttribute('style')
        if style:
            attrs += ' style="{}"'.format(style)
        return attrs.strip()

    def __copy__(self) -> 'HTMLElement':
        clone = super().__copy__()
        clone.style.update(self.style)
        return clone

    @property
    def end_tag(self) -> str:
        if self.tag in HTML_EMPTY:
            return ''
        else:
            return super().end_tag

    # Special propertyies for attribute
    @property
    def draggable(self) -> bool:
        return bool(self.getAttribute('draggable'))

    @draggable.setter
    def draggable(self, value:bool):
        self.setAttribute('draggable', value)

    @property
    def hidden(self) -> bool:
        return bool(self.getAttribute('hidden'))

    @hidden.setter
    def hidden(self, value:bool):
        self.setAttribute('hidden', value)

    @property
    def title(self) -> str:
        return self.getAttribute('title')

    @title.setter
    def title(self, value:str):
        self.setAttribute('title', value)

    @property
    def style(self) -> CSSStyleDeclaration:
        return self._style

    @style.setter
    def style(self, style:str):
        if isinstance(style, str):
            self._style._parse_str(style)
        elif style is None:
            self._style._parse_str('')
        elif isinstance(style, CSSStyleDeclaration):
            self._style._owner = None
            style._owner = self
            self._style = style
            self._style.update()
        else:
            raise TypeError('Invalid type for style: {}'.format(type(style)))

    def getAttribute(self, attr:str) -> str:
        if attr == 'style':
            # if style is neither None nor empty, return None
            # otherwise, return style.cssText
            if self.style:
                return self.style.cssText
            else:
                return None
        else:
            return super().getAttribute(attr)

    def _set_attribute(self, attr:str, value:str):
        if attr == 'style':
            self.style = value
        else:
            super()._set_attribute(attr, value)

    def _remove_attribute(self, attr:str):
        if attr == 'style':
            self.style = None
        else:
            super()._remove_attribute(attr)
