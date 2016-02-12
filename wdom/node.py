#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Iterable
from xml.dom.minicompat import NodeList
from xml.dom import Node
from xml.etree.ElementTree import HTML_EMPTY
import html

from wdom.css import parse_style_decl, CSSStyleDeclaration


class DOMTokenList(list):
    def __init__(self, *args):
        super().__init__()
        self.append(args)

    def _validate_token(self, token:str):
        if ' ' in token:
            raise ValueError(
                'Token contains space characters, which are invalid.')

    def append(self, token):
        if isinstance(token, str):
            for t in token.split(' '):
                self.add(t)
        elif isinstance(token, Iterable):
            for t in token:
                self.append(t)
        elif token is None:
            pass
        else:
            raise TypeError

    @property
    def length(self) -> int:
        return len(self)

    def add(self, token:str):
        self._validate_token(token)
        if token and token not in self:
            super().append(token)

    def remove(self, token:str):
        self._validate_token(token)
        if token in self:
            super().remove(token)

    def toggle(self, token:str):
        self._validate_token(token)
        if token in self:
            super().remove(token)
        else:
            super().append(token)

    def item(self, index:int) -> str:
        if 0 <= index < len(self):
            return self[index]
        else:
            return None

    def contains(self, token:str) -> bool:
        self._validate_token(token)
        return token in self

    def to_string(self) -> str:
        return ' '.join(self)


class NamedNodeMap(dict):
    @property
    def length(self) -> int:
        return len(self)

    def getNamedItem(self, name:str):
        return self.get(name, None)

    def setNamedItem(self, item: 'Attr'):
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        self[item.name] = item

    def removeNamedItem(self, name:str):
        return self.pop(name, None)

    def item(self, index:int):
        if 0 <= index < len(self):
            return self[tuple(self.keys())[index]]
        else:
            return None


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

    def __init__(self, parent=None) -> None:
        self.children = NodeList()
        self.parent = None
        if parent is not None:
            parent.appendChild(self)

    def __len__(self) -> int:
        return self.length

    def __contains__(self, other: Node) -> bool:
        return other in self.children

    def __copy__(self):
        clone = type(self)()
        return clone

    def __deepcopy__(self, memo=None):
        clone = self.__copy__()
        for child in self.childNodes:
            clone.appendChild(child.__deepcopy__(memo))
        return clone

    # DOM Level 1
    @property
    def length(self) -> int:
        return len(self.children)

    @property
    def parentNode(self) -> Node:
        return self.parent

    @property
    def childNodes(self) -> NodeList:
        return self.children

    @property
    def firstChild(self) -> Node:
        if self.hasChildNodes():
            return self.childNodes[0]
        else:
            return None

    @property
    def lastChild(self) -> Node:
        if self.hasChildNodes():
            return self.childNodes[-1]
        else:
            return None

    @property
    def previousSibling(self) -> Node:
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent.childNodes.index(self) - 1)

    @property
    def nextSibling(self) -> Node:
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent.childNodes.index(self) + 1)

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
    def _append_document_fragment(self, node):
        for c in tuple(node.childNodes):
            self._append_child(c)

    def _append_element(self, node):
        if node.parentNode is not None:
            node.remove()
        self.children.append(node)
        node.parent = self

    def _append_child(self, node) -> None:
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            self._append_document_fragment(node)
        else:
            self._append_element(node)

    def appendChild(self, node):
        self._append_child(node)

    def index(self, node):
        return self.children.index(node)

    def _insert_document_fragment_before(self, node, ref_node):
        for c in tuple(node.childNodes):
            self._insert_before(c, ref_node)

    def _insert_element_before(self, node, ref_node):
        if node.parentNode is not None:
            node.remove()
        self.children.insert(self.index(ref_node), node)
        node.parent = self

    def _insert_before(self, node, ref_node):
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            self._insert_document_fragment_before(node, ref_node)
        else:
            self._insert_element_before(node, ref_node)

    def insertBefore(self, node, ref_node) -> None:
        self._insert_before(node, ref_node)

    def hasChildNodes(self) -> bool:
        return bool(self.children)

    def _remove_child(self, node):
        if node not in self.children:
            raise ValueError('node to be removed is not a child of this node.')
        self.childNodes.remove(node)
        node.parent = None

    def removeChild(self, node):
        self._remove_child(node)

    def _replace_child(self, new_child: Node, old_child: Node):
        self._insert_before(new_child, old_child)
        self._remove_child(old_child)

    def replaceChild(self, new_child: Node, old_child: Node) -> None:
        self._replace_child(new_child, old_child)

    def hasAttributes(self) -> bool:
        return bool(self.attributes)

    def cloneNode(self, deep=False):
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
        for child in tuple(self.childNodes):
            self.removeChild(child)

    def empty(self):
        self._empty()

    def _get_text_content(self) -> str:
        return ''.join(child.textContent for child in self.childNodes)

    def _set_text_content(self, value:str):
        self._empty()
        if value:
            self.appendChild(Text(value))

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
    def value(self, val) -> None:
        self._value = val

    @property
    def isId(self) -> bool:
        return self.name.lower() == 'id'

    @property
    def textContent(self) -> str:
        return self.value

    @textContent.setter
    def textContent(self, val) -> None:
        self.value = val

    @property
    def childNodes(self) -> NodeList:
        return NodeList()

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


class Text(Node):
    nodeType = Node.TEXT_NODE
    nodeName = '#text'

    # DOM Level 1
    length = 0
    firstChild = None
    lastChild = None
    specified = False

    def __init__(self, text:str, parent=None):
        super().__init__(parent=parent)
        self._value = text

    @property
    def html(self) -> str:
        return self.textContent

    def _get_text_content(self):
        return html.escape(self._value)

    def _set_text_content(self, value:str):
        self._value = value

    @property
    def childNodes(self) -> NodeList:
        return NodeList()

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


class RawHtml(Text):
    '''Very similar to ``Text`` class, but contents are not escaped. Used for
    inner contents of ``<script>`` element or ``<style>`` element.'''
    @property
    def html(self) -> str:
        return self._value

    def _get_text_content(self) -> str:
        return self._value

    def _set_text_content(self, value:str):
        self._value = value


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
    def html(self):
        return '<!DOCTYPE {}>'.format(self.name)


class appendTextMixin:
    def _append_child(self, node):
        if isinstance(node, str):
            node = Text(node)
        elif not isinstance(node, Node):
            raise TypeError('Invalid type to append: {}'.format(node))

        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            self._append_document_fragment(node)
        elif node.nodeType in (Node.ELEMENT_NODE, Node.TEXT_NODE,
                               Node.DOCUMENT_TYPE_NODE):
            self._append_element(node)
        else:
            raise TypeError('Invalid type to append: {}'.format(node))

    def _insert_before(self, node, ref_node):
        if isinstance(node, str):
            node = Text(node)
        elif not isinstance(node, Node):
            raise TypeError('Invalid type to insert: {}'.format(node))

        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            self._insert_document_fragment_before(node, ref_node)
        elif node.nodeType in (Node.ELEMENT_NODE, Node.TEXT_NODE,
                               Node.DOCUMENT_TYPE_NODE):
            self._insert_element_before(node, ref_node)
        else:
            raise TypeError('Invalid type to insert: {}'.format(node))


class Element(appendTextMixin, Node):
    nodeType = Node.ELEMENT_NODE
    nodeValue = None

    def __init__(self, tag:str='', parent=None, **kwargs):
        super().__init__(parent=parent)
        self.tag = tag
        self.attributes = NamedNodeMap()
        self.classList = DOMTokenList()

        if 'class_' in kwargs:
            kwargs['class'] = kwargs.pop('class_')
        for k, v in kwargs.items():
            self.setAttribute(k, v)

    def __copy__(self):
        clone = super().__copy__()
        for attr in self.attributes.values():
            clone.setAttributeNode(attr)
        return clone

    def _get_attrs_by_string(self) -> str:
        attrs = ' '.join(attr.html for attr in self.attributes.values())
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
        return ''.join(child.html for child in self.childNodes)

    def _set_inner_html(self, html:str):
        self._empty()
        self.appendChild(RawHtml(html))

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
    def outerHTML(self):
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

    def getAttribute(self, attr:str):
        if attr == 'class':
            if self.classList:
                return self.classList.to_string()
            else:
                return None
        attr = self.getAttributeNode(attr)
        if attr is None:
            return None
        else:
            return attr.value

    def getAttributeNode(self, attr:str):
        return self.attributes.getNamedItem(attr)

    def hasAttribute(self, attr:str):
        if attr == 'class':
            return bool(self.classList)
        else:
            return attr in self.attributes

    def hasAttributes(self) -> bool:
        return bool(self.attributes) or bool(self.classList)

    def setAttribute(self, attr:str, value=None):
        if attr == 'class':
            self.classList = DOMTokenList(value)
        else:
            new_attr = Attr(attr, value)
            self.setAttributeNode(new_attr)

    def setAttributeNode(self, attr:Attr):
        self.attributes.setNamedItem(attr)

    def removeAttribute(self, attr:str):
        if attr == 'class':
            self.classList = DOMTokenList()
        else:
            self.attributes.removeNamedItem(attr)

    def removeAttributeNode(self, attr:Attr):
        self.attributes.removeNamedItem(attr.name)

    def getElementsByTagName(self, tag:str):
        elements = []
        tag = tag.upper()
        for child in self.childNodes:
            if child.tagName == tag:
                elements.append(child)
            if isinstance(child, Element):
                elements.extend(child.getElementsByTagName(tag))
        return elements


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
        return ''.join(child.html for child in self.childNodes)


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
        return ''.join(child.html for child in self.childNodes)


class HTMLElement(Element):
    def __init__(self, *args, style:str=None, **kwargs):
        self.style = style
        super().__init__(*args, **kwargs)

    def _get_attrs_by_string(self) -> str:
        attrs = super()._get_attrs_by_string()
        style = self.getAttribute('style')
        if style:
            attrs += ' style="{}"'.format(style)
        return attrs.strip()

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
            self._style = parse_style_decl(style)
        elif style is None:
            self._style = CSSStyleDeclaration()
        else:
            self._style = style

    def getAttribute(self, attr:str):
        if attr == 'style':
            # if style is neither None nor empty, return None
            # otherwise, return style.cssText
            if self.style:
                return self.style.cssText
            else:
                return None
        else:
            return super().getAttribute(attr)

    def setAttribute(self, attr:str, value:str):
        if attr == 'style':
            self.style = value
        else:
            super().setAttribute(attr, value)

    def removeAttribute(self, attr:str):
        if attr == 'style':
            self.style = None
        else:
            super().removeAttribute(attr)
