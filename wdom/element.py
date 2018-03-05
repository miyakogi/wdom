#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Conclete implemententions for Element node."""

from collections import OrderedDict, UserDict
import html as html_
from typing import Any, Callable, Dict, Iterable, Iterator, List
from typing import MutableSequence, Optional, Tuple, Type, Union
from typing import TYPE_CHECKING
from weakref import WeakSet, WeakValueDictionary
from xml.etree.ElementTree import HTML_EMPTY  # type: ignore

from wdom.css import CSSStyleDeclaration
from wdom.event import EventTarget, Event
from wdom.node import AbstractNode, Node, ParentNode, NonDocumentTypeChildNode
from wdom.node import DocumentFragment, NodeList, ChildNode
from wdom.parser import FragmentParser

if TYPE_CHECKING:
    from typing import MutableMapping  # noqa

_AttrValueType = Union[List[str], str, int, bool, CSSStyleDeclaration, None]


class DOMTokenList(MutableSequence[str]):
    """Collection of DOM token strings.

    DOM token is a string which does not contain spases.
    This class is mainly used for class list.
    """

    def __init__(self, owner: Union[Node, Type['HTMLElement']],
                 *args: Union[str, 'DOMTokenList']) -> None:
        """Initialize with owner node (maybe type of node) and initial values.

        :arg owner: Node/Node-class which has this collection.
        :arg args: space-separated string or iterable of tokens.
        """
        self._list = list()  # type: List[str]
        self._owner = owner
        self._append(args)

    def __len__(self) -> int:
        return len(self._list)

    def __contains__(self, item: object) -> bool:
        return item in self._list

    def __iter__(self) -> Iterator[str]:
        for token in self._list:
            yield token

    def _validate_token(self, token: str) -> None:
        if not isinstance(token, str):
            raise TypeError(
                'Token must be str, but {} passed.'.format(type(token)))
        if ' ' in token:
            raise ValueError(
                'Token contains space characters, which are invalid.')

    def _append(self, token: Union[Iterable, str]) -> None:
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

    def __getitem__(self, index: Union[int, slice]  # type: ignore
                    ) -> Optional[str]:
        if isinstance(index, slice):
            TypeError('slicing is not supported.')
        elif 0 <= index < len(self._list):
            return self._list[index]
        return None

    def __setitem__(self, s, item) -> None:  # type: ignore
        raise NotImplementedError

    def __delitem__(self, index: int) -> None:  # type: ignore
        raise NotImplementedError

    @property
    def length(self) -> int:
        """Get number of DOM token in this list."""
        return self.__len__()

    def add(self, *tokens: str) -> None:
        """Add new tokens to list."""
        from wdom.web_node import WdomElement
        _new_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token and token not in self:
                self._list.append(token)
                _new_tokens.append(token)
        if isinstance(self._owner, WdomElement) and _new_tokens:
            self._owner.js_exec('addClass', _new_tokens)  # type: ignore

    def remove(self, *tokens: str) -> None:
        """Remove tokens from list."""
        from wdom.web_node import WdomElement
        _removed_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token in self:
                self._list.remove(token)
                _removed_tokens.append(token)
        if isinstance(self._owner, WdomElement) and _removed_tokens:
            self._owner.js_exec('removeClass', _removed_tokens)  # type: ignore

    def toggle(self, token: str) -> None:
        """Add or remove token to/from list.

        If token is in this list, the token will be removed. Otherwise add it
        to list.
        """
        self._validate_token(token)
        if token in self:
            self.remove(token)
        else:
            self.add(token)

    def item(self, index: int) -> Optional[str]:
        """Return the token of the ``index``.

        ``index`` must be 0 or positive integer. If index is out of range,
        return None.
        """
        return self[index]

    def insert(self, index: int, item: str) -> None:
        """Not implemented."""
        raise NotImplementedError

    def contains(self, token: str) -> bool:
        """Return if the token is in the list or not."""
        self._validate_token(token)
        return token in self

    def toString(self) -> str:
        """Return string representation of this list.

        Actually it will be a spase-separated tokens.
        """
        return ' '.join(self)


class Attr:
    """Attribute node.

    In the latest DOM specification, Attr interface does not inherits ``Node``
    interface. (Previously, Attr inherited Node interface.)
    """

    def __init__(self, name: str,
                 value: _AttrValueType = None,
                 owner: Node = None) -> None:
        """Initialize this attribute.

        :arg str name: property name.
        :arg _AttrValueType value: attribute value.
        :arg Node owner: owner node of this attribute (optional).
        """
        self._name = name.lower()
        self._value = value
        self._owner = owner

    @property
    def html(self) -> str:
        """Return string representation of this.

        Used in start tag of HTML representation of the Element node.
        """
        if self._owner and self.name in self._owner._special_attr_boolean:
            return self.name
        else:
            value = self.value
            if isinstance(value, str):
                value = html_.escape(value)
            return '{name}="{value}"'.format(name=self.name, value=value)

    @property
    def name(self) -> str:
        """Name of this attr."""
        return self._name

    @property
    def value(self) -> _AttrValueType:
        """Value of this attr."""
        return self._value or ''

    @value.setter
    def value(self, val: str) -> None:
        self._value = val

    @property
    def isId(self) -> bool:
        """Return True if this Attr is an ID node (name is ``id``)."""
        return self.name.lower() == 'id'


class DraggableAttr(Attr):
    """Attribute node class for draggable attribute."""

    @property
    def html(self) -> str:
        """Return html representation."""
        if isinstance(self.value, bool):
            val = 'true' if self.value else 'false'
        else:
            val = str(self.value)
        return 'draggable="{}"'.format(val)


class NamedNodeMap(UserDict):
    """Collection of Attr objects."""

    def __init__(self, owner: Node) -> None:
        """Initialize with owner node.

        :arg Node owner: owner node of this object.
        """
        self._owner = owner
        self._dict = OrderedDict()  # type: OrderedDict[str, Attr]

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, item: object) -> bool:
        return item in self._dict

    def __getitem__(self, index: Union[int, str]) -> Optional[Attr]:
        if isinstance(index, int):
            return tuple(self._dict.values())[index]
        return None

    def __setitem__(self, attr: str, item: Attr) -> None:
        self._dict[attr] = item

    def __delitem__(self, attr: str) -> None:
        del self._dict[attr]

    def __iter__(self) -> Iterator[str]:
        for attr in self._dict.keys():
            yield attr

    @property
    def length(self) -> int:
        """Return number of Attrs in this collection."""
        return len(self)

    def getNamedItem(self, name: str) -> Optional[Attr]:
        """Get ``Attr`` object which has ``name``.

        If does not have ``name`` attr, return None.
        """
        return self._dict.get(name, None)

    def setNamedItem(self, item: Attr) -> None:
        """Set ``Attr`` object in this collection."""
        from wdom.web_node import WdomElement
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WdomElement):
            self._owner.js_exec('setAttribute', item.name,  # type: ignore
                                item.value)
        self._dict[item.name] = item
        item._owner = self._owner

    def removeNamedItem(self, item: Attr) -> Optional[Attr]:
        """Set ``Attr`` object and return it (if exists)."""
        from wdom.web_node import WdomElement
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WdomElement):
            self._owner.js_exec('removeAttribute', item.name)
        removed_item = self._dict.pop(item.name, None)
        if removed_item:
            removed_item._owner = self._owner
        return removed_item

    def item(self, index: int) -> Optional[Attr]:
        """Return ``index``-th attr node."""
        if 0 <= index < len(self):
            return self._dict[tuple(self._dict.keys())[index]]
        return None

    def toString(self) -> str:
        """Return string representation of collections."""
        return ' '.join(attr.html for attr in self._dict.values())


class ElementParser(FragmentParser):
    """HTML Parser class whose default nodes are ``Element``."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.default_class = Element


class HTMLElementParser(ElementParser):
    """HTML Parser class whose default nodes are ``HTMLElement``."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.default_class = HTMLElement


_str_attr_doc = '''
Getter: Get value of ``{attr}`` attribute of this element, as string. If
`{attr}` is not defined, return empty string.
Setter: Set the value of
``{attr}`` attribute of this element.
Deleter: Remove ``{attr}`` attribute from this element.
'''

_bool_attr_doc = '''
Getter: Return True if this element has ``{attr}`` attribute. Otherwise return
False.
Setter: If True, add ``{attr}`` attribute to this element. Otherwise remove
``{attr}``.
Deleter: Remove ``{attr}`` attribute from this element.
'''


def _string_properties(attr: str) -> property:
    def getter(self: Node) -> str:
        return self.getAttribute(attr) or ''

    def setter(self: Node, value: str) -> None:
        self.setAttribute(attr, str(value))

    def deleter(self: Node) -> None:
        self.removeAttribute(attr)

    return property(getter, setter, deleter, _str_attr_doc.format(attr=attr))


def _boolean_properties(attr: str) -> property:
    def getter(self: Node) -> bool:
        return bool(self.getAttribute(attr))

    def setter(self: Node, value: bool) -> None:
        if value:
            self.setAttribute(attr, True)
        else:
            self.removeAttribute(attr)

    def deleter(self: Node) -> None:
        self.removeAttribute(attr)

    return property(getter, setter, deleter, _bool_attr_doc.format(attr=attr))


class ElementMeta(type):
    """Metaclass for Element class."""

    def __new__(cls: type, name: str, bases: Tuple[type],
                namespace: Dict[str, Any], **kwargs: Any) -> type:
        """Add special properties to new class."""
        for attr in namespace.get('_special_attr_string', []):
            namespace[attr] = _string_properties(attr)
        for attr in namespace.get('_special_attr_boolean', []):
            namespace[attr] = _boolean_properties(attr)
        new_cls = super().__new__(cls, name, bases, dict(namespace))
        return new_cls


def getElementsBy(start_node: ParentNode,
                  cond: Callable[['Element'], bool]) -> NodeList:
    """Return list of child elements of start_node which matches ``cond``.

    ``cond`` must be a function which gets a single argument ``Element``,
    and returns boolean. If the node matches requested condition, ``cond``
    should return True.
    This searches all child elements recursively.

    :arg ParentNode start_node:
    :arg cond: Callable[[Element], bool]
    :rtype: NodeList[Element]
    """
    elements = []
    for child in start_node.children:
        if cond(child):
            elements.append(child)
        elements.extend(child.getElementsBy(cond))
    return NodeList(elements)


def getElementsByTagName(start_node: ParentNode, tag: str) -> NodeList:
    """Get child nodes which tag name is ``tag``."""
    _tag = tag.upper()
    return getElementsBy(start_node, lambda node: node.tagName == _tag)


def getElementsByClassName(start_node: ParentNode, class_name: str
                           ) -> NodeList:
    """Get child nodes which has ``class_name`` class attribute."""
    classes = set(class_name.split(' '))
    return getElementsBy(
        start_node,
        lambda node: classes.issubset(set(node.classList))
    )


def querySelector(start_node: ParentNode, selectors: str) -> AbstractNode:
    """Not Implemented yet.

    Please use `getElementsBy` method instead.
    """
    raise NotImplementedError


def querySelectorAll(start_node: ParentNode, selectors: str) -> NodeList:
    """Not Implemented yet.

    Please use `getElementsBy` method instead.
    """
    raise NotImplementedError


class Element(Node, EventTarget, ParentNode, NonDocumentTypeChildNode,
              ChildNode, metaclass=ElementMeta):
    """Element base class."""

    nodeType = Node.ELEMENT_NODE
    nodeValue = None
    _parser_class = ElementParser  # type: Type[ElementParser]
    _element_buffer = WeakSet()  # type: WeakSet[Node]
    _elements_with_id = WeakValueDictionary()  # type: MutableMapping
    _should_escape_text = True
    _special_attr_string = ['id']
    _special_attr_boolean = []  # type: List[str]

    def __init__(self, tag: str='', parent: Node = None,
                 _registered: bool = True, **kwargs: Any) -> None:
        """Initialize.

        :arg str tag: HTML tag of this node.
        :arg Node parent: Parent node of this node.
        :arg bool _registered: Is registered to CustomElementRegistry.
        :arg kwargs: key-value pair of attributes.
        """
        super().__init__(parent=parent)
        self._registered = _registered
        self.tag = tag
        self._element_buffer.add(self)  # used to suport custom elements
        self.attributes = NamedNodeMap(self)
        self.classList = DOMTokenList(self)

        if 'class_' in kwargs:
            kwargs['class'] = kwargs.pop('class_')
        if 'is_' in kwargs:
            kwargs['is'] = kwargs.pop('is_')
        for k, v in kwargs.items():
            self.setAttribute(k, v)

    def _clone_node(self) -> 'Element':
        clone = type(self)(self.tag)
        for attr in self.attributes:
            clone.setAttribute(attr, self.getAttribute(attr))
        # TODO: should clone event listeners???
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
        """Return HTML start tag."""
        tag = '<' + self.tag
        attrs = self._get_attrs_by_string()
        if attrs:
            tag = ' '.join((tag, attrs))
        return tag + '>'

    @property
    def end_tag(self) -> str:
        """Return HTML end tag."""
        return '</{}>'.format(self.tag)

    def _parse_html(self, html: str) -> DocumentFragment:
        parser = self._parser_class()
        parser.feed(html)
        return parser.root

    def _get_inner_html(self) -> str:
        return ''.join(child.html for child in self.childNodes)

    def _set_inner_html(self, html: str) -> None:
        self._empty()
        self._append_child(self._parse_html(html))

    @property
    def innerHTML(self) -> str:
        """Return HTML representation of child nodes."""
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html: str) -> None:
        """Remove all child nodes and set ``html`` as new contents.

        ``html`` is parsed to ``Element`` nodes and set as child nodes.
        """
        self._set_inner_html(html)

    @property
    def html(self) -> str:
        """Return HTML representation of this node."""
        return self.start_tag + self.innerHTML + self.end_tag

    def insertAdjacentHTML(self, position: str, html: str) -> None:
        """Parse ``html`` to DOM and insert to ``position``.

        ``position`` is a case-insensive string, and must be one of
        "beforeBegin", "afterBegin", "beforeEnd", or "afterEnd".
        """
        df = self._parse_html(html)
        pos = position.lower()
        if pos == 'beforebegin':
            self.before(df)
        elif pos == 'afterbegin':
            self.prepend(df)
        elif pos == 'beforeend':
            self.append(df)
        elif pos == 'afterend':
            self.after(df)
        else:
            raise ValueError(
                'The value provided ({}) is not one of "beforeBegin", '
                '"afterBegin", "beforeEnd", or "afterEnd".'.format(position)
            )

    @property
    def outerHTML(self) -> str:
        """Return html representation of this node.

        Equivalent to ``self.html``.
        """
        return self.html

    @property
    def nodeName(self) -> str:  # type: ignore
        """Return tag name (capital case)."""
        return self.tag.upper()

    @property
    def tagName(self) -> str:
        """Return tag name (capital case)."""
        return self.tag.upper()

    @property
    def localName(self) -> str:
        """Return tag name (lower case)."""
        return self.tag.lower()

    @property
    def className(self) -> str:
        """Get/Set class name as/by string."""
        return self.getAttribute('class') or ''  # type: ignore

    @className.setter
    def className(self, new_class: str) -> None:
        if not isinstance(new_class, str):
            raise TypeError('className must be str.')
        self.setAttribute('class', new_class)

    def getAttribute(self, attr: str) -> _AttrValueType:
        """Get attribute of this node as string format.

        If this node does not have ``attr``, return None.
        """
        if attr == 'class':
            if self.classList:
                return self.classList.toString()
            return None
        attr_node = self.getAttributeNode(attr)
        if attr_node is None:
            return None
        return attr_node.value

    def getAttributeNode(self, attr: str) -> Optional[Attr]:
        """Get attribute of this node as Attr format.

        If this node does not have ``attr``, return None.
        """
        return self.attributes.getNamedItem(attr)

    def hasAttribute(self, attr: str) -> bool:
        """Return True if this node has ``attr``."""
        if attr == 'class':
            return bool(self.classList)
        return attr in self.attributes

    def hasAttributes(self) -> bool:
        """Return True if this node has any attributes."""
        return bool(self.attributes) or bool(self.classList)

    def _set_attribute_class(self, value: _AttrValueType) -> None:
        if isinstance(value, str):
            self.classList = DOMTokenList(self, value)
        elif isinstance(value, Iterable):
            self.classList = DOMTokenList(self, *value)
        else:
            raise TypeError(
                'class attribute must be str, '
                'but got {}'.format(type(value))
            )

    def _change_id(self, value: _AttrValueType) -> None:
        if 'id' in self.attributes:
            # remove old reference to self
            self._elements_with_id.pop(self.id, None)
        # register this elements with new id
        if isinstance(value, (int, str)):
            self._elements_with_id[value] = self
        else:
            raise TypeError(
                'id attribute must be int or integer-string.'
            )

    def _set_attribute(self, attr: str, value: _AttrValueType) -> None:
        if attr == 'class':
            self._set_attribute_class(value)
        else:
            if attr == 'id':
                self._change_id(value)
            if not attr == 'draggable':
                attr_cls = Attr
            else:
                attr_cls = DraggableAttr
            new_attr_node = attr_cls(attr, value)
            self.setAttributeNode(new_attr_node)

    def setAttribute(self, attr: str, value: _AttrValueType) -> None:
        """Set ``attr`` and ``value`` in this node."""
        self._set_attribute(attr, value)

    def setAttributeNode(self, attr: Attr) -> None:
        """Set ``Attr`` node as this node's attribute."""
        self.attributes.setNamedItem(attr)

    def _remove_attribute(self, attr: str) -> None:
        if attr == 'class':
            self.classList = DOMTokenList(self)
        else:
            if attr == 'id':
                self._elements_with_id.pop(self.id, None)
            _attr = self.getAttributeNode(attr)
            if _attr:
                self.attributes.removeNamedItem(_attr)

    def removeAttribute(self, attr: str) -> None:
        """Remove ``attr`` from this node."""
        self._remove_attribute(attr)

    def removeAttributeNode(self, attr: Attr) -> Optional[Attr]:
        """Remove ``Attr`` node from this node."""
        return self.attributes.removeNamedItem(attr)

    def getElementsBy(self, cond: Callable[['Element'], bool]) -> NodeList:
        """Get elements under this node which matches condition."""
        return getElementsBy(self, cond)

    def getElementsByTagName(self, tag: str) -> NodeList:
        """Get elements with tag name under this node."""
        return getElementsByTagName(self, tag)

    def getElementsByClassName(self, class_name: str) -> NodeList:
        """Get elements with class name under this node."""
        return getElementsByClassName(self, class_name)

    def querySelector(self, selectors: str) -> Node:
        """Not Implemented."""
        return querySelector(self, selectors)

    def querySelectorAll(self, selectors: str) -> NodeList:
        """Not Implemented."""
        return querySelectorAll(self, selectors)


class HTMLElement(Element):
    """Base class for HTMLElement.

    This class extends `Element` class with some HTML specific features.
    """

    _special_attr_string = ['title', 'type']
    _special_attr_boolean = ['hidden']
    _parser_class = HTMLElementParser  # type: Type[ElementParser]

    def __init__(self, *args: Any, style: str=None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__style = CSSStyleDeclaration(style, owner=self)

    def _get_attrs_by_string(self) -> str:
        attrs = super()._get_attrs_by_string()
        style = self.getAttribute('style')
        if style:
            attrs += ' style="{}"'.format(style)
        return attrs.strip()

    def _clone_node(self) -> 'HTMLElement':
        clone = super()._clone_node()
        clone.style.update(self.style)
        return clone

    @property
    def end_tag(self) -> str:
        """Retrun html end tag.

        If tag is empty tag like <img> or <br>, return empty string.
        """
        if self.tag in HTML_EMPTY:
            return ''
        return super().end_tag

    @property
    def style(self) -> CSSStyleDeclaration:
        """Return style attribute of this node."""
        return self.__style

    @style.setter
    def style(self, style: _AttrValueType) -> None:
        """Set style attribute of this node.

        If argument ``style`` is string, it will be parsed to
        ``CSSStyleDeclaration``.
        """
        if isinstance(style, str):
            self.__style._parse_str(style)
        elif style is None:
            self.__style._parse_str('')
        elif isinstance(style, CSSStyleDeclaration):
            self.__style._owner = None
            if style._owner is not None:
                new_style = CSSStyleDeclaration(owner=self)
                new_style.update(style)
                self.__style = new_style
            else:
                # always making new decl may be better
                style._owner = self
                self.__style = style
        else:
            raise TypeError('Invalid type for style: {}'.format(type(style)))

    @property
    def draggable(self) -> Union[bool, str]:
        """Get ``draggable`` property."""
        if not self.hasAttribute('draggable'):
            return False
        return self.getAttribute('draggable')  # type: ignore

    @draggable.setter
    def draggable(self, value: Union[bool, str]) -> None:
        """Set ``draggable`` property.

        ``value`` is boolean or string.
        """
        if value is False:
            self.removeAttribute('draggable')
        else:
            self.setAttribute('draggable', value)

    def getAttribute(self, attr: str) -> _AttrValueType:  # noqa: D102
        if attr == 'style':
            # if style is neither None nor empty, return None
            # otherwise, return style.cssText
            if self.style:
                return self.style.cssText
            return None
        return super().getAttribute(attr)

    def _set_attribute(self, attr: str, value: _AttrValueType) -> None:
        if attr == 'style':
            self.style = value  # type: ignore
        else:
            super()._set_attribute(attr, value)  # type: ignore

    def _remove_attribute(self, attr: str) -> None:
        if attr == 'style':
            self.style = None  # type: ignore
        else:
            super()._remove_attribute(attr)  # type: ignore


class FormControlMixin(AbstractNode):
    """Mixin class for FormControl classes."""

    def __init__(self, *args: Any, form: Union[str, 'HTMLFormElement'] = None,
                 **kwargs: Any) -> None:
        """``form`` is a ``HTMLFormElement`` object or id of it."""
        super().__init__(*args, **kwargs)  # type: ignore
        self.__form = None
        from wdom.document import getElementById
        if isinstance(form, str):
            form = getElementById(form)
        if isinstance(form, HTMLFormElement):
            self.__form = form
        elif form is not None:
            raise TypeError(
                '"form" attribute must be an HTMLFormElement or id of'
                'HTMLFormElement in the same document.'
            )

    @property
    def form(self) -> Optional['HTMLFormElement']:
        """Get ``HTMLFormElement`` object related to this node."""
        if self.__form:
            return self.__form
        parent = self.parentNode
        while parent:
            if isinstance(parent, HTMLFormElement):
                return parent
            else:
                parent = parent.parentNode
        return None


class HTMLAnchorElement(HTMLElement):  # noqa: D204
    """HTMLAnchorElement class (<a></a> tag)."""
    _special_attr_string = ['href', 'name', 'rel', 'src', 'target']


class HTMLButtonElement(HTMLElement):  # noqa: D204
    """HTMLButtonElement class (<button></button> tag)."""
    _special_attr_string = ['name', 'value']
    _special_attr_boolean = ['disabled']


class HTMLFormElement(HTMLElement):  # noqa: D204
    """HTMLFormElement class (<form></form> tag)."""
    _special_attr_string = ['name']


class HTMLIFrameElement(HTMLElement):  # noqa: D204
    """HTMLIFrameElement class (<iframe></iframe> tag)."""
    _special_attr_string = ['height', 'name', 'src', 'target', 'width']


class HTMLInputElement(HTMLElement, FormControlMixin):
    """HTMLInputElement class (<input></input> tag)."""

    _special_attr_string = ['height', 'name', 'src', 'value', 'width']
    _special_attr_boolean = ['checked', 'disabled', 'multiple', 'readonly',
                             'required']

    def on_event_pre(self, e: Event) -> None:
        """Set values set on browser before calling event listeners."""
        super().on_event_pre(e)
        ct_msg = e.init.get('currentTarget', dict())
        if e.type in ('input', 'change'):
            # Update user inputs
            if self.type.lower() == 'checkbox':
                self._set_attribute('checked', ct_msg.get('checked'))
            elif self.type.lower() == 'radio':
                self._set_attribute('checked', ct_msg.get('checked'))
                for other in self._find_grouped_nodes():
                    if other is not self:
                        other._remove_attribute('checked')
            else:
                self._set_attribute('value', ct_msg.get('value'))

    @property
    def defaultChecked(self) -> bool:
        """Property is this control checked by default."""
        return bool(self.getAttribute('defaultChecked'))

    @defaultChecked.setter
    def defaultChecked(self, value: bool) -> None:
        if value:
            self.setAttribute('defaultChecked', True)
            self.checked = True
        else:
            self.removeAttribute('defaultChecked')
            self.checked = False

    @property
    def defaultValue(self) -> _AttrValueType:
        """Defatul value of this node."""
        return self.getAttribute('defaultValue')

    @defaultValue.setter
    def defaultValue(self, value: str) -> None:
        self.setAttribute('defaultValue', value)
        self.value = value

    def _is_same_group(self, node: Element) -> bool:
        tag = self.tagName
        name = self.getAttribute('name')
        return (tag == node.tagName and
                node is not self and
                name == node.getAttribute('name'))

    def _find_root(self) -> Node:
        doc = self.ownerDocument
        if doc is not None:
            return doc
        p = self
        while p.parentNode is not None:
            p = p.parentNode
        return p

    def _find_grouped_nodes(self) -> NodeList:
        p = self._find_root()
        return p.getElementsBy(self._is_same_group)


class HTMLLabelElement(HTMLElement, FormControlMixin):
    """HTMLLabelElement class (<label></label> tag)."""

    @property
    def htmlFor(self) -> _AttrValueType:
        """Retrun ``for`` attribute value."""
        return self.getAttribute('for')

    @htmlFor.setter
    def htmlFor(self, value: str) -> None:
        self.setAttribute('for', value)

    @property
    def control(self) -> Optional[HTMLElement]:
        """Return related HTMLElement object."""
        id = self.getAttribute('for')
        if id:
            if self.ownerDocument:
                return self.ownerDocument.getElementById(id)
            elif isinstance(id, str):
                from wdom.document import getElementById
                return getElementById(id)
            else:
                raise TypeError('"for" attribute must be string')
        return None


class HTMLOptGroupElement(HTMLElement, FormControlMixin):  # noqa: D204
    """HTMLOptionElement class (<optgroup></optgroup> tag)."""
    _special_attr_string = ['label']
    _special_attr_boolean = ['disabled']


class HTMLOptionElement(HTMLElement, FormControlMixin):  # noqa: D204
    """HTMLOptionElement class (<option></option> tag)."""
    _special_attr_string = ['label', 'value']
    _special_attr_boolean = ['defaultSelected', 'disabled', 'selected']


class HTMLScriptElement(HTMLElement):  # noqa: D204
    """HTMLScriptElement class (<script></script> tag).

    In this tag, all inner contents are not escaped.
    """
    _special_attr_string = ['charset', 'src']
    _special_attr_boolean = ['async', 'defer']
    _should_escape_text = False


class HTMLSelectElement(HTMLElement, FormControlMixin):
    """HTMLSelectElement class (<select></select> tag)."""

    _special_attr_string = ['name', 'size', 'value']
    _special_attr_boolean = ['disabled', 'multiple', 'required']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._selected_options = []  # type: List[str]
        super().__init__(*args, **kwargs)

    def on_event_pre(self, e: Event) -> None:
        """Set values set on browser before calling event listeners."""
        super().on_event_pre(e)
        ct_msg = e.init.get('currentTarget', dict())
        if e.type in ('input', 'change'):
            self._set_attribute('value', ct_msg.get('value'))
            _selected = ct_msg.get('selectedOptions', [])
            self._selected_options.clear()
            for opt in self.options:
                if opt.wdom_id in _selected:
                    self._selected_options.append(opt)
                    opt._set_attribute('selected', True)
                else:
                    opt._remove_attribute('selected')

    @property
    def length(self) -> int:
        """Return number of options in this node."""
        return len(self.options)

    @property
    def options(self) -> NodeList:
        """Return all option nodes in this node."""
        return self.getElementsByTagName('option')

    @property
    def selectedOptions(self) -> NodeList:
        """Return all selected option nodes."""
        return NodeList(list(opt for opt in self.options if opt.selected))


class HTMLStyleElement(HTMLElement):  # noqa: D204
    """HTMLStyleElement class (<style></style> tag).

    In this tag, all inner contents are not escaped.
    """
    _special_attr_boolean = ['disabled', 'scoped']
    _should_escape_text = False


class HTMLTextAreaElement(HTMLElement, FormControlMixin):  # noqa: D204
    """HTMLTextAreaElement class (<textarea></textarea> tag)."""
    _special_attr_string = ['height', 'name', 'src', 'value', 'width']
    _special_attr_boolean = ['disabled']
    defaultValue = HTMLElement.textContent

    def on_event_pre(self, e: Event) -> None:
        """Set values set on browser before calling event listeners."""
        super().on_event_pre(e)
        ct_msg = e.init.get('currentTarget', dict())
        if e.type in ('input', 'change'):
            # Update user inputs
            self._set_text_content(ct_msg.get('value') or '')
