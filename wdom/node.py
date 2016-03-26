#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Iterable, OrderedDict
from xml.etree.ElementTree import HTML_EMPTY
import html
from typing import Union, Tuple

from wdom.css import CSSStyleDeclaration
from wdom.event import EventTarget
from wdom.interface import WebIF, Node


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

    def to_string(self) -> str:
        return ' '.join(self)


class NamedNodeMap:
    def __init__(self, owner):
        self._owner = owner
        self._dict = OrderedDict()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, item:str) -> bool:
        return item in self._dict

    def __getitem__(self, index: Union[int, str]) -> 'Attr':
        if isinstance(index, int):
            return tuple(self._dict.values())[index]
        else:
            return None

    def __iter__(self) -> 'Attr':
        for attr in self._dict.keys():
            yield attr

    @property
    def length(self) -> int:
        return len(self)

    def getNamedItem(self, name:str) -> 'Attr':
        return self._dict.get(name, None)

    def setNamedItem(self, item: 'Attr'):
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('setAttribute', attr=item.name,
                                value=item.value)
        self._dict[item.name] = item

    def removeNamedItem(self, item:'Attr') -> 'Attr':
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('removeAttribute', attr=item.name)
        return self._dict.pop(item.name, None)

    def item(self, index:int) -> 'Attr':
        if 0 <= index < len(self):
            return self._dict[tuple(self._dict.keys())[index]]
        else:
            return None

    def toString(self) -> str:
        return ' '.join(attr.html for attr in self._dict.values())


class NodeList:
    def __init__(self, ref:list):
        self.ref = ref

    def __getitem__(self, index:int) -> Node:
        return self.item(index)

    def __len__(self) -> int:
        return len(self.ref)

    def __iter__(self) -> Node:
        for n in self.ref:
            yield n

    @property
    def length(self) -> int:
        return len(self)

    def item(self, index:int) -> Node:
        if not isinstance(index, int):
            raise TypeError(
                'Indeces must be integer, not {}'.format(type(index)))
        return self.ref[index] if 0 <= index < self.length else None


class HTMLCollection(NodeList):
    def namedItem(self, name:str) -> Node:
        for n in self.ref:
            if n.getAttribute('id') == name:
                return n
        for n in self.ref:
            if n.getAttribute('name') == name:
                return n


class Node(Node):
    # DOM Level 1
    nodeType = None
    nodeName = ''
    nodeValue = ''
    attributes = None

    # DOM Level 2
    namespaceURI = ''
    prefix = ''

    # DOM Level 3
    baseURI = ''

    # DOM Level 4
    parentElement = None

    def __init__(self, parent=None):
        super().__init__()  # Need to call init in multiple inheritce
        self._children = list()
        self._parent = None
        if parent is not None:
            parent.appendChild(self)

    def __len__(self) -> int:
        return self.length

    def __contains__(self, other: Node) -> bool:
        return other in self._children

    def __copy__(self) -> Node:
        clone = type(self)()
        return clone

    def __deepcopy__(self, memo=None) -> Node:
        clone = self.__copy__()
        for child in self.childNodes:
            clone.appendChild(child.__deepcopy__(memo))
        return clone

    # DOM Level 1
    @property
    def length(self) -> int:
        return len(self._children)

    @property
    def parentNode(self) -> Node:
        return self._parent

    @property
    def childNodes(self) -> NodeList:
        return NodeList(self._children)

    @property
    def firstChild(self) -> Node:
        if self.hasChildNodes():
            return self._children[0]
        else:
            return None

    @property
    def lastChild(self) -> Node:
        if self.hasChildNodes():
            return self._children[-1]
        else:
            return None

    @property
    def previousSibling(self) -> Node:
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent._children.index(self) - 1)

    @property
    def nextSibling(self) -> Node:
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent._children.index(self) + 1)

    # DOM Level 2
    @property
    def ownerDocument(self) -> Node:
        if self.nodeType == Node.DOCUMENT_NODE:
            return self
        elif self.parentNode is not None:
            return self.parentNode.ownerDocument
        else:
            return None

    # Methods
    def _append_document_fragment(self, node) -> Node:
        for c in tuple(node._children):
            self._append_child(c)
        return node

    def _append_element(self, node) -> Node:
        if node.parentNode is not None:
            node.remove()
        self._children.append(node)
        node._parent = self
        return node

    def _append_child(self, node) -> Node:
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._append_document_fragment(node)
        else:
            return self._append_element(node)

    def appendChild(self, node) -> Node:
        return self._append_child(node)

    def index(self, node):
        return self._children.index(node)

    def _insert_document_fragment_before(self, node, ref_node) -> Node:
        for c in tuple(node._children):
            self._insert_before(c, ref_node)
        return node

    def _insert_element_before(self, node, ref_node) -> Node:
        if node.parentNode is not None:
            node.remove()
        self._children.insert(self.index(ref_node), node)
        node._parent = self
        return node

    def _insert_before(self, node, ref_node) -> Node:
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._insert_document_fragment_before(node, ref_node)
        else:
            return self._insert_element_before(node, ref_node)

    def insertBefore(self, node, ref_node) -> Node:
        return self._insert_before(node, ref_node)

    def hasChildNodes(self) -> bool:
        return bool(self._children)

    def _remove_child(self, node) -> Node:
        if node not in self._children:
            raise ValueError('node to be removed is not a child of this node.')
        self._children.remove(node)
        node._parent = None
        return node

    def removeChild(self, node) -> Node:
        return self._remove_child(node)

    def _replace_child(self, new_child: Node, old_child: Node) -> Node:
        self._insert_before(new_child, old_child)
        return self._remove_child(old_child)

    def replaceChild(self, new_child: Node, old_child: Node) -> Node:
        return self._replace_child(new_child, old_child)

    def hasAttributes(self) -> bool:
        return bool(self.attributes)

    def cloneNode(self, deep=False) -> Node:
        if deep:
            return self.__deepcopy__()
        else:
            return self.__copy__()

    def _remove(self):
        if self.parentNode is not None:
            self.parentNode.removeChild(self)

    def remove(self):
        self._remove()

    def _empty(self):
        for child in tuple(self._children):
            self.removeChild(child)

    def empty(self):
        self._empty()

    def _get_text_content(self) -> str:
        return ''.join(child.textContent for child in self._children)

    def _set_text_content(self, value:str):
        self._empty()
        if value:
            self._append_child(Text(value))

    @property
    def textContent(self) -> str:
        return self._get_text_content()

    @textContent.setter
    def textContent(self, value:str):
        self._set_text_content(value)


class Attr(Node):
    nodeType = Node.ATTRIBUTE_NODE
    _child_node_types = ()
    _boolean_attrs = (
        'async', 'autofocus', 'autoplay', 'checked', 'contenteditable',
        'defer', 'disabled', 'draggable', 'dropzone', 'formnovalidate',
        'hidden', 'ismap', 'loop', 'multiple', 'muted', 'novalidate',
        'readonly', 'required', 'reversed', 'spellcheck', 'scoped', 'selected',
    )

    # DOM Level 1
    length = 0
    parentNode = None
    firstChild = None
    lastChild = None
    previousSibling = None
    nextSibling = None
    ownerDocument = None
    specified = True

    def __init__(self, name:str, value=None) -> None:
        self._name = name
        self._value = value

    @property
    def html(self) -> str:
        if self.name in self._boolean_attrs:
            return self.name if self.value else ''
        else:
            return '{name}="{value}"'.format(name=self.name, value=self.value)

    @property
    def nodeName(self) -> str:
        return self.name

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

    @property
    def textContent(self) -> str:
        return self.value

    @textContent.setter
    def textContent(self, val):
        self.value = val

    @property
    def childNodes(self) -> NodeList:
        return NodeList([])

    # Methods
    def appendChild(self, node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def insertBefore(self, node, ref_node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def hasChildNodes(self) -> bool:
        return False

    def removeChild(self, node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def replaceChild(self, old_child: Node, new_child: Node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def hasAttributes(self) -> bool:
        return False


class CharacterData(Node):
    # DOM Level 1
    firstChild = None
    lastChild = None
    specified = False

    def __init__(self, text:str='', parent=None):
        super().__init__(parent=parent)
        self.data = text

    def __copy__(self):
        clone = type(self)(self.data)
        return clone

    @property
    def html(self) -> str:
        return self.textContent

    def _get_text_content(self) -> str:
        return self.data

    def _set_text_content(self, value:str):
        self.data = value

    def __len__(self) -> int:
        return len(self.data)

    @property
    def length(self) -> int:
        return len(self)

    def _append_data(self, string:str):
        self.data += string

    def appendData(self, string:str):
        self._append_data(string)

    def _insert_data(self, offset:int, string:str):
        self.data = ''.join((self.data[:offset], string, self.data[offset:]))

    def insertData(self, offset:int, string:str):
        self._insert_data(offset, string)

    def _delete_data(self, offset:int, count:int):
        self.data = ''.join((self.data[:offset], self.data[offset+count:]))

    def deleteData(self, offset:int, count:int):
        self._delete_data(offset, count)

    def _replace_data(self, offset:int, count:int, string:str):
        self.data = ''.join((
            self.data[:offset], string, self.data[offset+count:]))

    def replaceData(self, offset:int, count:int, string:str):
        self._replace_data(offset, count, string)

    @property
    def childNodes(self) -> NodeList:
        return NodeList([])

    # Methods
    def appendChild(self, node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def insertBefore(self, node, ref_node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def hasChildNodes(self) -> bool:
        return False

    def removeChild(self, node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def replaceChild(self, old_child: Node, new_child: Node) -> None:
        raise NotImplementedError('This node does not support this method.')

    def hasAttributes(self) -> bool:
        return False


class Text(CharacterData):
    nodeType = Node.TEXT_NODE
    nodeName = '#text'

    @property
    def html(self) -> str:
        return html.escape(self.data)


class RawHtml(Text):
    '''Very similar to ``Text`` class, but contents are not escaped. Used for
    inner contents of ``<script>`` element or ``<style>`` element.'''
    @property
    def html(self) -> str:
        return self.data


class Comment(CharacterData):
    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'

    @property
    def html(self) -> str:
        return ''.join(('<!--', self.data, '-->'))


class DocumentType(Node):
    nodeType = Node.DOCUMENT_TYPE_NODE
    nodeValue = None
    textContent = None

    @property
    def nodeName(self) -> str:
        return self.name

    def __init__(self, type='html', parent=None):
        super().__init__(parent=parent)
        self._type = type

    @property
    def name(self) -> str:
        return self._type

    @name.setter
    def name(self, name:str):
        self._type = name

    @property
    def html(self) -> str:
        return '<!DOCTYPE {}>'.format(self.name)


class appendTextMixin:
    def _append_child(self, node) -> Node:
        if isinstance(node, str):
            node = Text(node)
        elif not isinstance(node, Node):
            raise TypeError('Invalid type to append: {}'.format(node))

        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._append_document_fragment(node)
        elif node.nodeType in (Node.ELEMENT_NODE, Node.TEXT_NODE,
                               Node.DOCUMENT_TYPE_NODE, Node.COMMENT_NODE):
            return self._append_element(node)
        else:
            raise TypeError('Invalid type to append: {}'.format(node))

    def _insert_before(self, node, ref_node) -> Node:
        if isinstance(node, str):
            node = Text(node)
        elif not isinstance(node, Node):
            raise TypeError('Invalid type to insert: {}'.format(node))

        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._insert_document_fragment_before(node, ref_node)
        elif node.nodeType in (Node.ELEMENT_NODE, Node.TEXT_NODE,
                               Node.DOCUMENT_TYPE_NODE, Node.COMMENT_NODE):
            return self._insert_element_before(node, ref_node)
        else:
            raise TypeError('Invalid type to insert: {}'.format(node))


class Element(appendTextMixin, Node, EventTarget):
    nodeType = Node.ELEMENT_NODE
    nodeValue = None

    def __init__(self, tag:str='', parent=None, **kwargs):
        super().__init__(parent=parent)
        self.tag = tag
        self.attributes = NamedNodeMap(self)
        self.classList = DOMTokenList(self)

        if 'class_' in kwargs:
            kwargs['class'] = kwargs.pop('class_')
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
        self._append_child(RawHtml(html))

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
                return self.classList.to_string()
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


class DocumentFragment(appendTextMixin, Node):
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = '#document-fragment'
    parentNode = None
    previousSibling = None
    nextSibling = None

    def __init__(self, *args):
        super().__init__()
        for arg in args:
            self.appendChild(arg)

    @property
    def html(self) -> str:
        return ''.join(child.html for child in self._children)


class Document(Node):
    nodeType = Node.DOCUMENT_NODE
    nodeName = '#document'

    def __init__(self, doctype='html', title='', charset=''):
        super().__init__()
        self.doctype = DocumentType(doctype)
        self.appendChild(self.doctype)

        self.html = HTMLElement('html', parent=self)

        self.head = HTMLElement('head', parent=self.html)
        self.charset_element = HTMLElement('meta', parent=self.head)
        self.charset = charset
        self.title_element = HTMLElement('title', parent=self.head)
        self.title = title

        self.body = HTMLElement('body', parent=self.html)

    @property
    def title(self) -> str:
        return self.title_element.textContent

    @title.setter
    def title(self, value:str):
        self.title_element.textContent = value

    @property
    def charset(self) -> str:
        return self.charset_element.getAttribute('charset')

    @charset.setter
    def charset(self, value:str):
        self.charset_element.setAttribute('charset', value)

    def render(self) -> str:
        return ''.join(child.html for child in self._children)


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
