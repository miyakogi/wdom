#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Node related basic interface/classes."""

import html
import logging
from typing import TYPE_CHECKING
from typing import Any, Iterator, Optional, Sequence, Union

from xml.dom import Node as _Node

if TYPE_CHECKING:
    from typing import List  # noqa
    from wdom.element import Element  # noqa

logger = logging.getLogger(__name__)


class AbstractNode(_Node):
    """Abstract Base Class for Node classes."""

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


class Node(AbstractNode):
    """Base Class for Node interface."""

    @property
    def connected(self) -> bool:
        """When this instance has any connection, return True."""
        return False

    def __init__(self, parent: AbstractNode = None) -> None:
        """Initialize node object with parent node.

        :param Node parent: parent node.
        """
        super().__init__()  # Need to call init in multiple inheritce
        self.__children = list()  # type: List[Node]
        self.__parent = None
        if parent:
            parent.appendChild(self)

    def __bool__(self) -> bool:
        """Return always True."""
        return True

    def __len__(self) -> int:
        """Return number of child nodes."""
        return self.length

    def __contains__(self, other: AbstractNode) -> bool:
        return other in self.__children

    # DOM Level 1
    @property
    def length(self) -> int:
        """Return number of child nodes."""
        return len(self.childNodes)

    @property
    def parentNode(self) -> Optional[AbstractNode]:
        """Return parent node.

        If this node does not have a parent, return ``None``.
        """
        return self.__parent

    @property
    def childNodes(self) -> 'NodeList':
        """Return child nodes of this node.

        Returned object is an instance of NodeList, which is a list like object
        but not support any modification. NodeList is a **live object**, which
        means that changes on this node is reflected to the object.
        """
        return NodeList(self.__children)

    @property
    def firstChild(self) -> Optional[AbstractNode]:
        """Return the first child node.

        If this node does not have any child, return ``None``.
        """
        if self.hasChildNodes():
            return self.childNodes[0]
        return None

    @property
    def lastChild(self) -> Optional[AbstractNode]:
        """Return the last child node.

        If this node does not have any child, return ``None``.
        """
        if self.hasChildNodes():
            return self.childNodes[-1]
        return None

    @property
    def previousSibling(self) -> Optional[AbstractNode]:
        """Return the previous sibling of this node.

        If there is no previous sibling, return ``None``.
        """
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent.childNodes.index(self) - 1)

    @property
    def nextSibling(self) -> Optional[AbstractNode]:
        """Return the next sibling of this node.

        If there is no next sibling, return ``None``.
        """
        parent = self.parentNode
        if parent is None:
            return None
        return parent.childNodes.item(parent.childNodes.index(self) + 1)

    # DOM Level 2
    @property
    def ownerDocument(self) -> Optional[AbstractNode]:
        """Return the owner document of this node.

        Owner document is an ancestor document node of this node. If this node
        (or node tree including this node) is not appended to any document
        node, this property returns ``None``.

        :rtype: Document or None
        """
        if self.nodeType == Node.DOCUMENT_NODE:
            return self
        elif self.parentNode:
            return self.parentNode.ownerDocument
        return None

    # Methods
    def _append_document_fragment(self, node: AbstractNode) -> AbstractNode:
        for c in tuple(node.childNodes):
            self._append_child(c)
        return node

    def _append_element(self, node: AbstractNode) -> AbstractNode:
        if node.parentNode:
            node.parentNode.removeChild(node)
        self.__children.append(node)
        node.__parent = self
        return node

    def _append_child(self, node: AbstractNode) -> AbstractNode:
        if not isinstance(node, Node):
            raise TypeError(
                'appndChild() only accepts a Node instance, but get {}. '
                'If you want to add string or mupltiple nodes once, '
                'use append() method instead.'.format(type(node)))
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._append_document_fragment(node)
        return self._append_element(node)

    def appendChild(self, node: AbstractNode) -> AbstractNode:
        """Append the node at the last of this child nodes."""
        return self._append_child(node)

    def index(self, node: AbstractNode) -> int:
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

    def _insert_document_fragment_before(self, node: AbstractNode,
                                         ref_node: AbstractNode
                                         ) -> AbstractNode:
        for c in tuple(node.childNodes):
            self._insert_before(c, ref_node)
        return node

    def _insert_element_before(self, node: AbstractNode,
                               ref_node: AbstractNode) -> AbstractNode:
        if node.parentNode:
            node.parentNode.removeChild(node)
        self.__children.insert(self.index(ref_node), node)
        node.__parent = self
        return node

    def _insert_before(self, node: AbstractNode, ref_node:
                       AbstractNode) -> AbstractNode:
        if not isinstance(node, Node):
            raise TypeError(
                'insertBefore() only accepts a Node instance, but get {}.'
                'If you want to insert string or mupltiple nodes, '
                'use ref_node.before() instead.'.format(type(node)))
        if node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return self._insert_document_fragment_before(node, ref_node)
        return self._insert_element_before(node, ref_node)

    def insertBefore(self, node: AbstractNode,
                     ref_node: AbstractNode) -> AbstractNode:
        """Insert a node just before the reference node."""
        return self._insert_before(node, ref_node)

    def hasChildNodes(self) -> bool:
        """Return True if this node has child nodes, otherwise return False."""
        return bool(self.childNodes)

    def _remove_child(self, node: AbstractNode) -> AbstractNode:
        if node not in self.__children:
            raise ValueError('node to be removed is not a child of this node.')
        self.__children.remove(node)
        node.__parent = None
        return node

    def removeChild(self, node: AbstractNode) -> AbstractNode:
        """Remove a node from this node.

        If node is not a child of this node, raise ``ValueError``.
        """
        return self._remove_child(node)

    def _replace_child(self, new_child: AbstractNode,
                       old_child: AbstractNode) -> AbstractNode:
        self._insert_before(new_child, old_child)
        return self._remove_child(old_child)

    def replaceChild(self, new_child: AbstractNode,
                     old_child: AbstractNode) -> AbstractNode:
        """Replace an old child with new child."""
        return self._replace_child(new_child, old_child)

    def hasAttributes(self) -> bool:
        """Return True if this node has attributes."""
        return hasattr(self, 'attributes') and bool(self.attributes)

    def _clone_node(self) -> 'Node':
        clone = type(self)()
        return clone

    def _clone_node_deep(self) -> 'Node':
        clone = self._clone_node()
        for child in self.childNodes:
            clone.appendChild(child._clone_node_deep())
        return clone

    def cloneNode(self, deep: bool=False) -> AbstractNode:
        """Return new copy of this node.

        If optional argument ``deep`` is specified and is True, new node has
        clones of child nodes of this node (if presents).
        """
        if deep:
            return self._clone_node_deep()
        return self._clone_node()

    __copy__ = _clone_node  # alias

    def __deepcopy__(self, memo: Any) -> 'Node':
        return self.cloneNode(True)

    def _empty(self) -> None:
        for child in tuple(self.__children):
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
        """Return text contents of this node and all chid nodes.

        When any value is set to this property, all child nodes are removed and
        new value is set as a text node.
        """
        return self._get_text_content()

    @textContent.setter
    def textContent(self, value: str) -> None:
        """Remove all child nodes and set new text."""
        self._set_text_content(value)


class NodeList(Sequence[Node]):
    """Collection of Node objects."""

    def __init__(self, nodes: Sequence[Node]) -> None:
        """Initialize NodeList by iterable `nodes`."""
        self.__nodes = nodes

    def __getitem__(self, index: int) -> Node:  # type: ignore
        """Get `index`-th node."""
        return self.__nodes[index]

    def __len__(self) -> int:
        return len(self.__nodes)

    def __contains__(self, other: object) -> bool:
        return other in self.__nodes

    def __iter__(self) -> Iterator[AbstractNode]:
        for n in self.__nodes:
            yield n

    @property
    def length(self) -> int:
        """Return number of nodes in this list."""
        return len(self)

    def item(self, index: int) -> Optional[Node]:
        """Return item with the index.

        If the index is negative number or out of the list, return None.
        """
        if not isinstance(index, int):
            raise TypeError(
                'Indeces must be integer, not {}'.format(type(index)))
        return self.__nodes[index] if 0 <= index < self.length else None

    def index(self, node: Node) -> int:  # type: ignore
        """Get index of the node."""
        return self.__nodes.index(node)


class HTMLCollection(NodeList):
    """Collection of HTML elements."""

    def namedItem(self, name: str) -> Optional[Node]:
        """TODO."""
        for n in self:
            if n.getAttribute('id') == name:
                return n
        for n in self:
            if n.getAttribute('name') == name:
                return n
        return None


def _ensure_node(node: Union[str, AbstractNode]) -> AbstractNode:
    """Ensure to be node.

    If ``node`` is string, convert it to ``Text`` node.
    """
    if isinstance(node, str):
        return Text(node)
    elif isinstance(node, Node):
        return node
    else:
        raise TypeError('Invalid type to append: {}'.format(node))


def _to_node_list(nodes: Sequence[Union[str, AbstractNode]]) -> AbstractNode:
    if len(nodes) == 1:
        return _ensure_node(nodes[0])
    df = DocumentFragment()
    for n in nodes:
        df.appendChild(_ensure_node(n))
    return df


class ParentNode(AbstractNode):
    """Mixin class for Node classes which can have child nodes.

    This class is inherited by Document, DocumentFragment, and Element class.
    """

    @property
    def children(self) -> NodeList:
        """Return list of child nodes.

        Currently this is not a live object.
        """
        return NodeList([e for e in self.childNodes
                         if e.nodeType == Node.ELEMENT_NODE])

    @property
    def firstElementChild(self) -> Optional[AbstractNode]:
        """First Element child node.

        If this node has no element child, return None.
        """
        for child in self.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                return child
        return None

    @property
    def lastElementChild(self) -> Optional[AbstractNode]:
        """Last Element child node.

        If this node has no element child, return None.
        """
        for child in reversed(self.childNodes):  # type: ignore
            if child.nodeType == Node.ELEMENT_NODE:
                return child
        return None

    def prepend(self, *nodes: Union[str, AbstractNode]) -> None:
        """Insert new nodes before first child node."""
        node = _to_node_list(nodes)
        if self.firstChild:
            self.insertBefore(node, self.firstChild)
        else:
            self.appendChild(node)

    def append(self, *nodes: Union[AbstractNode, str]) -> None:
        """Append new nodes after last child node."""
        node = _to_node_list(nodes)
        self.appendChild(node)


class NonDocumentTypeChildNode(AbstractNode):
    """Mixin class for ``CharacterData`` and ``DocumentType`` class."""

    @property
    def previousElementSibling(self) -> Optional[AbstractNode]:
        """Previous Element Node.

        If this node has no previous element node, return None.
        """
        if self.parentNode is None:
            return None
        siblings = self.parentNode.childNodes
        for i in range(siblings.index(self), 0, -1):
            n = siblings[i-1]
            if n.nodeType == Node.ELEMENT_NODE:
                return n
        return None

    @property
    def nextElementSibling(self) -> Optional[AbstractNode]:
        """Next Element Node.

        If this node has no next element node, return None.
        """
        if self.parentNode is None:
            return None
        siblings = self.parentNode.childNodes
        for i in range(siblings.index(self) + 1, len(siblings)):
            n = siblings[i]
            if n.nodeType == Node.ELEMENT_NODE:
                return n
        return None


class ChildNode(AbstractNode):
    """Mixin class for Node classes which can have parent node.

    This class is inherited by DocumentType, Element, and CharacterData
    (super class of Text, Comment, and RawHtml) classes.
    """

    def before(self, *nodes: Union[AbstractNode, str]) -> None:
        """Insert nodes before this node.

        If nodes contains ``str``, it will be converted to Text node.
        """
        if self.parentNode:
            node = _to_node_list(nodes)
            self.parentNode.insertBefore(node, self)  # type: ignore

    def after(self, *nodes: Union[AbstractNode, str]) -> None:
        """Append nodes after this node.

        If nodes contains ``str``, it will be converted to Text node.
        """
        if self.parentNode:
            node = _to_node_list(nodes)
            _next_node = self.nextSibling
            if _next_node is None:
                self.parentNode.appendChild(node)
            else:
                self.parentNode.insertBefore(node, _next_node)

    def replaceWith(self, *nodes: Union[AbstractNode, str]) -> None:
        """Replace this node with nodes.

        If nodes contains ``str``, it will be converted to Text node.
        """
        if self.parentNode:
            node = _to_node_list(nodes)
            self.parentNode.replaceChild(node, self)  # type: ignore

    def _remove(self) -> None:
        if self.parentNode:
            self.parentNode.removeChild(self)  # type: ignore

    def remove(self) -> None:
        """Remove this node from the parent node."""
        self._remove()


class CharacterData(Node, ChildNode, NonDocumentTypeChildNode):
    """Abstract class for classes which wraps text data.

    This class is a super class of ``Text`` and ``Comment``.
    """

    # DOM Level 1
    firstChild = None
    lastChild = None
    specified = False

    def __init__(self, text: str='', parent: Node = None) -> None:  # noqa
        super().__init__(parent=parent)
        self.data = text

    def _clone_node(self) -> 'CharacterData':
        clone = type(self)(self.data)
        return clone

    @property
    def html(self) -> str:
        """Return html representation of this node."""
        return self.textContent

    def _get_text_content(self) -> str:
        return self.data

    def _set_text_content(self, value: str) -> None:
        self.data = value

    def __len__(self) -> int:
        return len(self.data)

    @property
    def length(self) -> int:
        """Return length of content."""
        return len(self)

    def _append_data(self, string: str) -> None:
        self.data += string

    def appendData(self, string: str) -> None:
        """Add ``string`` to end of this node."""
        self._append_data(string)

    def _insert_data(self, offset: int, string: str) -> None:
        self.data = ''.join((self.data[:offset], string, self.data[offset:]))

    def insertData(self, offset: int, string: str) -> None:
        """Insert ``string`` at offset on this node."""
        self._insert_data(offset, string)

    def _delete_data(self, offset: int, count: int) -> None:
        self.data = ''.join((self.data[:offset], self.data[offset+count:]))

    def deleteData(self, offset: int, count: int) -> None:
        """Delete data by offset to count letters."""
        self._delete_data(offset, count)

    def _replace_data(self, offset: int, count: int, string: str) -> None:
        self.data = ''.join((
            self.data[:offset], string, self.data[offset+count:]))

    def replaceData(self, offset: int, count: int, string: str) -> None:
        """Replace data from offset to count by string."""
        self._replace_data(offset, count, string)

    @property
    def childNodes(self) -> NodeList:
        """Return child nodes.

        This node can't have child, so return empty ``NodeList`` object.
        """
        return NodeList([])

    # Methods
    def appendChild(self, node: Node) -> Node:
        """Not supported."""
        raise NotImplementedError('This node does not support this method.')

    def insertBefore(self, node: Node, ref_node: Node) -> Node:
        """Not supported."""
        raise NotImplementedError('This node does not support this method.')

    def hasChildNodes(self) -> bool:
        """Return false."""
        return False

    def removeChild(self, node: Node) -> Node:
        """Not supported."""
        raise NotImplementedError('This node does not support this method.')

    def replaceChild(self, new_child: Node, old_child: Node) -> Node:
        """Not supported."""
        raise NotImplementedError('This node does not support this method.')

    def hasAttributes(self) -> bool:
        """Return false."""
        return False


class Text(CharacterData):
    """Node class to wrap text contents."""

    nodeType = Node.TEXT_NODE
    nodeName = '#text'

    @property
    def html(self) -> str:
        """Return html-escaped string representation of this node."""
        if self.parentNode and self.parentNode._should_escape_text:
            return html.escape(self.data)
        return self.data


class RawHtml(Text):
    """Very similar to ``Text`` class, but contents are always not escaped.

    This node is [NOT DOM Standard].
    """

    @property
    def html(self) -> str:
        """Return html representation."""
        return self.data


class Comment(CharacterData):
    """Comment node class."""

    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'

    @property
    def html(self) -> str:
        """Return html representation."""
        return ''.join(('<!--', self.data, '-->'))


class DocumentType(Node, NonDocumentTypeChildNode):
    """DocumentType node class."""

    nodeType = Node.DOCUMENT_TYPE_NODE
    nodeValue = None
    textContent = None  # type: ignore
    _should_escape_text = True

    def _clone_node(self) -> 'CharacterData':
        clone = type(self)(self.name)
        return clone

    @property
    def nodeName(self) -> str:  # type: ignore
        """Return node name (=type)."""
        return self.name

    def __init__(self, type: str = 'html', parent: Node = None) -> None:
        """Initialize DocumentType node with `type` doctype."""
        super().__init__(parent=parent)
        self.__type = type

    @property
    def name(self) -> str:
        """Return node type."""
        return self.__type

    @name.setter
    def name(self, name: str) -> None:
        self.__type = name

    @property
    def html(self) -> str:
        """Return html representation."""
        return '<!DOCTYPE {}>'.format(self.name)


class DocumentFragment(Node, ParentNode):
    """DocumentFragument node class."""

    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = '#document-fragment'
    parentNode = None
    previousSibling = None
    nextSibling = None
    _should_escape_text = True

    @property
    def html(self) -> str:
        """Return html representation."""
        return ''.join(child.html for child in self.childNodes)
