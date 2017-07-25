#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html
from typing import TYPE_CHECKING
from typing import Union, Any, Optional, Sequence

from wdom.interface import NodeList
from wdom.interface import Node as _Node

if TYPE_CHECKING:
    from typing import List, Mapping, Any, Iterable  # noqa
    from wdom.element import NamedNodeMap  # noqa


class Node(_Node):
    """Base Abstract Class for Node interface."""
    # DOM Level 1
    nodeType = None
    nodeName = ''
    nodeValue = ''  # type: Optional[str]

    # DOM Level 2
    namespaceURI = ''
    prefix = ''

    # DOM Level 3
    baseURI = ''

    # DOM Level 4
    parentElement = None

    # should escape text contents
    _should_escape_text = False

    def __init__(self, parent: 'Node' = None) -> None:
        super().__init__()  # Need to call init in multiple inheritce
        self._children = list()  # type: List[Node]
        self._parent = None
        if parent:
            parent.appendChild(self)

    def __bool__(self) -> bool:
        """Return always True."""
        return True

    def __len__(self) -> int:
        """Return number of child nodes."""
        return self.length

    def __contains__(self, other: 'Node') -> bool:
        return other in self._children

    def __copy__(self) -> 'Node':
        clone = type(self)()
        return clone

    def __deepcopy__(self, memo: Any = None) -> 'Node':
        clone = self.__copy__()
        for child in self.childNodes:
            clone.appendChild(child.__deepcopy__(memo))
        return clone

    # DOM Level 1
    @property
    def length(self) -> int:
        """Return number of child nodes."""
        return len(self.childNodes)

    @property
    def parentNode(self) -> Optional['Node']:
        """Return parent node.

        If this node does not have a parent, return ``None``.
        """
        return self._parent

    @property
    def childNodes(self) -> NodeList:
        """Return child nodes of this node.

        Returned object is an instance of NodeList, which is a list like object
        but not support any modification. NodeList is a **live object**, which
        means that changes on this node is reflected to the object.
        """
        return NodeList(self._children)

    @property
    def firstChild(self) -> Optional['Node']:
        """Return the first child node.

        If this node does not have any child, return ``None``.
        """
        if self.hasChildNodes():
            return self.childNodes[0]
        else:
            return None

    @property
    def lastChild(self) -> Optional['Node']:
        """Return the last child node.

        If this node does not have any child, return ``None``.
        """
        if self.hasChildNodes():
            return self.childNodes[-1]
        else:
            return None

    @property
    def previousSibling(self) -> Optional['Node']:
        """Return the previous sibling of this node.

        If there is no previous sibling, return ``None``.
        """
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent.childNodes.index(self) - 1)

    @property
    def nextSibling(self) -> Optional['Node']:
        """Return the next sibling of this node.

        If there is no next sibling, return ``None``.
        """
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent.childNodes.index(self) + 1)

    # DOM Level 2
    @property
    def ownerDocument(self) -> Optional['Node']:
        """Return the owner document of this node.

        Owner document is an ancestor document node of this node. If this node
        (or node tree including this node) is not appended to any document
        node, this property returns ``None``.
        """
        if self.nodeType == Node.DOCUMENT_NODE:
            return self
        elif self.parentNode:
            return self.parentNode.ownerDocument
        else:
            return None

    # Methods
    def _append_document_fragment(self, node: 'Node') -> 'Node':
        for c in tuple(node.childNodes):
            self._append_child(c)
        return node

    def _append_element(self, node: 'Node') -> 'Node':
        if node.parentNode:
            node.parentNode.removeChild(node)
        self._children.append(node)
        node._parent = self
        return node

    def _append_child(self, node: 'Node') -> 'Node':
        if not isinstance(node, Node):
            raise TypeError(
                'appndChild() only accepts a Node instance, but get {}. '
                'If you want to add string or mupltiple nodes once, '
                'use append() method instead.'.format(type(node)))
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._append_document_fragment(node)
        else:
            return self._append_element(node)

    def appendChild(self, node: 'Node') -> 'Node':
        """Append the node at the last of this child nodes."""
        return self._append_child(node)

    def index(self, node: 'Node') -> int:
        """Return index of the node.

        If the node is not a child of this node, raise ``ValueError``.
        """
        if node in self.childNodes:
            return self.childNodes.index(node)
        elif isinstance(node, Text):
            for i, n in enumerate(self.childNodes):
                # should consider multiple match?
                if isinstance(n, Text) and n.data == node:
                    return i
        raise ValueError('node is not in this node')

    def _insert_document_fragment_before(self, node: 'Node', ref_node: 'Node'
                                         ) -> 'Node':
        for c in tuple(node.childNodes):
            self._insert_before(c, ref_node)
        return node

    def _insert_element_before(self, node: 'Node', ref_node: 'Node') -> 'Node':
        if node.parentNode:
            node.parentNode.removeChild(node)
        self._children.insert(self.index(ref_node), node)
        node._parent = self
        return node

    def _insert_before(self, node: 'Node', ref_node: 'Node') -> 'Node':
        if not isinstance(node, Node):
            raise TypeError(
                'insertBefore() only accepts a Node instance, but get {}.'
                'If you want to insert string or mupltiple nodes, '
                'use ref_node.before() instead.'.format(type(node)))
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._insert_document_fragment_before(node, ref_node)
        else:
            return self._insert_element_before(node, ref_node)

    def insertBefore(self, node: 'Node', ref_node: 'Node') -> 'Node':
        """Insert a node just before the reference node."""
        return self._insert_before(node, ref_node)

    def hasChildNodes(self) -> bool:
        """Return True if this node has child nodes, otherwise return False."""
        return bool(self.childNodes)

    def _remove_child(self, node: 'Node') -> 'Node':
        if node not in self._children:
            raise ValueError('node to be removed is not a child of this node.')
        self._children.remove(node)
        node._parent = None
        return node

    def removeChild(self, node: 'Node') -> 'Node':
        """Remove a node from this node.

        If node is not a child of this node, raise ``ValueError``.
        """
        return self._remove_child(node)

    def _replace_child(self, new_child: 'Node', old_child: 'Node') -> 'Node':
        self._insert_before(new_child, old_child)
        return self._remove_child(old_child)

    def replaceChild(self, new_child: 'Node', old_child: 'Node') -> 'Node':
        """Replace an old child with new child."""
        return self._replace_child(new_child, old_child)

    def hasAttributes(self) -> bool:
        """Return True if this node has attributes."""
        return hasattr(self, 'attributes') and bool(self.attributes)

    def cloneNode(self, deep: bool=False) -> 'Node':
        """Return new copy of this node.

        If optional argument ``deep`` is specified and is True, new node has
        clones of child nodes of this node (if presents).
        """
        if deep:
            return self.__deepcopy__()
        else:
            return self.__copy__()

    def _empty(self) -> None:
        for child in tuple(self._children):
            self._remove_child(child)

    def empty(self) -> None:
        """[Not Standard] Remove all child nodes from this node.

        This is equivalent to ``node.textContent = ''``.
        """
        self._empty()

    def _get_text_content(self) -> str:
        return ''.join(child.textContent for child in self.childNodes)

    def _set_text_content(self, value: str) -> None:
        self._empty()
        if value:
            self._append_child(Text(value))

    @property
    def textContent(self) -> str:
        '''Return text contents of this node and all chid nodes. When any value
        is set to this property, all child nodes are removed and new value is
        set as a text node.
        '''
        return self._get_text_content()

    @textContent.setter
    def textContent(self, value: str) -> None:
        """Remove all child nodes and set new text."""
        self._set_text_content(value)


def _ensure_node(node: Union[str, 'Node']) -> 'Node':
    if isinstance(node, str):
        return Text(node)
    elif isinstance(node, Node):
        return node
    else:
        raise TypeError('Invalid type to append: {}'.format(node))


def _to_node_list(nodes: Sequence[Union[str, 'Node']]) -> 'Node':
    if len(nodes) == 1:
        return _ensure_node(nodes[0])
    else:
        df = DocumentFragment()
        for n in nodes:
            df.appendChild(_ensure_node(n))
        return df


class ParentNode:
    """[DOM Level 4] Mixin class for Document, DocumentFragment, and Element.
    """
    @property
    def children(self) -> NodeList:
        """Currently this is not a live object"""
        return NodeList([e for e in self.childNodes  # type: ignore
                         if e.nodeType == Node.ELEMENT_NODE])

    @property
    def firstElementChild(self) -> Optional[Node]:  # type: ignore
        """First Element child node.

        If this node has no element child, return None.
        """
        for child in self.childNodes:  # type: ignore
            if child.nodeType == Node.ELEMENT_NODE:
                return child

    @property
    def lastElementChild(self) -> Optional[Node]:  # type: ignore
        """Last Element child node.

        If this node has no element child, return None.
        """
        for child in reversed(self.childNodes):  # type: ignore
            if child.nodeType == Node.ELEMENT_NODE:
                return child

    def prepend(self, *nodes: Union[str, Node]) -> None:
        """Insert new nodes before first child node."""
        node = _to_node_list(nodes)
        if self.firstChild:  # type: ignore
            self.insertBefore(node, self.firstChild)  # type: ignore
        else:
            self.appendChild(node)  # type: ignore

    def append(self, *nodes: Union['Node', str]) -> None:
        """Append new nodes after last child node."""
        node = _to_node_list(nodes)
        self.appendChild(node)  # type: ignore

    def query(self, relativeSelectors: str) -> Node:
        raise NotImplementedError

    def queryAll(self, relativeSelectors: str) -> NodeList:
        raise NotImplementedError

    def querySelector(self, selectors: str) -> Node:
        raise NotImplementedError

    def querySelectorAll(self, selectors: str) -> NodeList:
        raise NotImplementedError


class NonDocumentTypeChildNode:

    @property
    def previousElementSibling(self) -> Optional[Node]:  # type: ignore
        """Previous Element Node.

        If this node has no previous element node, return None.
        """
        if self.parentNode is None:  # type: ignore
            return None
        siblings = self.parentNode.childNodes  # type: ignore
        for i in range(siblings.index(self), 0, -1):
            n = siblings[i-1]
            if n.nodeType == Node.ELEMENT_NODE:
                return n

    @property
    def nextElementSibling(self) -> Optional[Node]:  # type: ignore
        """Next Element Node.

        If this node has no next element node, return None.
        """
        if self.parentNode is None:  # type: ignore
            return None
        siblings = self.parentNode.childNodes  # type: ignore
        for i in range(siblings.index(self) + 1, len(siblings)):
            n = siblings[i]
            if n.nodeType == Node.ELEMENT_NODE:
                return n


class ChildNode:
    """[DOM Level 4] Mixin class for DocumentType, Element, and CharacterData
    (Text, RawHTML, Comment).
    """

    def before(self, *nodes: Union[Node, str]) -> None:
        """Insert nodes before this node.

        If nodes contains ``str``, it will be converted to Text node.
        """
        if self.parentNode:  # type: ignore
            node = _to_node_list(nodes)
            self.parentNode.insertBefore(node, self)  # type: ignore

    def after(self, *nodes: Union[Node, str]) -> None:
        """Append nodes after this node.

        If nodes contains ``str``, it will be converted to Text node.
        """
        if self.parentNode:  # type: ignore
            node = _to_node_list(nodes)
            _next_node = self.nextSibling  # type: ignore
            if _next_node is None:
                self.parentNode.appendChild(node)  # type: ignore
            else:
                self.parentNode.insertBefore(node, _next_node)  # type: ignore

    def replaceWith(self, *nodes: Union[Node, str]) -> None:
        """Replace this node with nodes.

        If nodes contains ``str``, it will be converted to Text node.
        """
        if self.parentNode:  # type: ignore
            node = _to_node_list(nodes)
            self.parentNode.replaceChild(node, self)  # type: ignore

    def _remove(self) -> None:
        if self.parentNode:  # type: ignore
            self.parentNode.removeChild(self)  # type: ignore

    def remove(self) -> None:
        """Remove this node from the parent node."""
        self._remove()


class CharacterData(Node, ChildNode, NonDocumentTypeChildNode):
    # DOM Level 1
    firstChild = None
    lastChild = None
    specified = False

    def __init__(self, text: str='', parent: Node = None) -> None:
        super().__init__(parent=parent)
        self.data = text

    def __copy__(self) -> 'CharacterData':
        clone = type(self)(self.data)
        return clone

    @property
    def html(self) -> str:
        return self.textContent

    def _get_text_content(self) -> str:
        return self.data

    def _set_text_content(self, value: str) -> None:
        self.data = value

    def __len__(self) -> int:
        return len(self.data)

    @property
    def length(self) -> int:
        return len(self)

    def _append_data(self, string: str) -> None:
        self.data += string

    def appendData(self, string: str) -> None:
        self._append_data(string)

    def _insert_data(self, offset: int, string: str) -> None:
        self.data = ''.join((self.data[:offset], string, self.data[offset:]))

    def insertData(self, offset: int, string: str) -> None:
        self._insert_data(offset, string)

    def _delete_data(self, offset: int, count: int) -> None:
        self.data = ''.join((self.data[:offset], self.data[offset+count:]))

    def deleteData(self, offset: int, count: int) -> None:
        self._delete_data(offset, count)

    def _replace_data(self, offset: int, count: int, string: str) -> None:
        self.data = ''.join((
            self.data[:offset], string, self.data[offset+count:]))

    def replaceData(self, offset: int, count: int, string: str) -> None:
        self._replace_data(offset, count, string)

    @property
    def childNodes(self) -> NodeList:
        return NodeList([])

    # Methods
    def appendChild(self, node: Node) -> Node:
        raise NotImplementedError('This node does not support this method.')

    def insertBefore(self, node: Node, ref_node: Node) -> Node:
        raise NotImplementedError('This node does not support this method.')

    def hasChildNodes(self) -> bool:
        return False

    def removeChild(self, node: Node) -> Node:
        raise NotImplementedError('This node does not support this method.')

    def replaceChild(self, new_child: Node, old_child: Node) -> Node:
        raise NotImplementedError('This node does not support this method.')

    def hasAttributes(self) -> bool:
        return False


class Text(CharacterData):
    nodeType = Node.TEXT_NODE
    nodeName = '#text'

    @property
    def html(self) -> str:
        if self.parentNode and self.parentNode._should_escape_text:
            return html.escape(self.data)
        else:
            return self.data


class RawHtml(Text):
    """Very similar to ``Text`` class, but contents are not escaped.

    Used for inner contents of ``<script>`` element or ``<style>`` element.
    """
    @property
    def html(self) -> str:
        return self.data


class Comment(CharacterData):
    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'

    @property
    def html(self) -> str:
        return ''.join(('<!--', self.data, '-->'))


class DocumentType(Node, NonDocumentTypeChildNode):
    nodeType = Node.DOCUMENT_TYPE_NODE
    nodeValue = None
    textContent = None  # type: ignore
    _should_escape_text = True

    @property
    def nodeName(self) -> str:  # type: ignore
        return self.name

    def __init__(self, type: str = 'html', parent: Optional[Node] = None
                 ) -> None:
        super().__init__(parent=parent)
        self._type = type

    @property
    def name(self) -> str:
        return self._type

    @name.setter
    def name(self, name: str) -> None:
        self._type = name

    @property
    def html(self) -> str:
        return '<!DOCTYPE {}>'.format(self.name)


class DocumentFragment(Node, ParentNode):
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = '#document-fragment'
    parentNode = None
    previousSibling = None
    nextSibling = None
    _should_escape_text = True

    @property
    def html(self) -> str:
        return ''.join(child.html for child in self.childNodes)
