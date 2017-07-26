#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict, UserDict
import html as html_
from typing import Union, Callable, Optional, Dict, Tuple
from typing import Iterable, MutableSequence
from typing import Any, Iterator, List, TYPE_CHECKING, Type
from weakref import WeakSet, WeakValueDictionary
from xml.etree.ElementTree import HTML_EMPTY  # type: ignore

from wdom.css import CSSStyleDeclaration
from wdom.event import EventTarget, Event
from wdom.node import Node, ParentNode, NonDocumentTypeChildNode, ChildNode
from wdom.node import DocumentFragment, NodeList
from wdom.parser import FragmentParser
from wdom.webif import WebIF

if TYPE_CHECKING:
    from typing import MutableMapping  # noqa
    from wdom.tag import Tag  # noqa

_AttrValueType = Union[List[str], str, int, bool, CSSStyleDeclaration, None]


class DOMTokenList(MutableSequence[str]):
    """List of DOM token.

    DOM token is a string which does not contain spases.
    """
    def __init__(self, owner: Union[Node, Type['Tag']],
                 *args: Union[str, 'DOMTokenList']) -> None:
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
        """Number of DOM token in this list."""
        return self.__len__()

    def add(self, *tokens: str) -> None:
        """Add new tokens to list."""
        _new_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token and token not in self:
                self._list.append(token)
                _new_tokens.append(token)
        if isinstance(self._owner, WebIF) and _new_tokens:
            self._owner.js_exec('addClass', _new_tokens)

    def remove(self, *tokens: str) -> None:
        """Remove tokens from list."""
        _removed_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token in self:
                self._list.remove(token)
                _removed_tokens.append(token)
        if isinstance(self._owner, WebIF) and _removed_tokens:
            self._owner.js_exec('removeClass', _removed_tokens)

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
    @property
    def html(self) -> str:
        if isinstance(self.value, bool):
            val = 'true' if self.value else 'false'
        else:
            val = str(self.value)
        return 'draggable="{}"'.format(val)


class NamedNodeMap(UserDict):
    def __init__(self, owner: Node) -> None:
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
        return len(self)

    def getNamedItem(self, name: str) -> Optional[Attr]:
        return self._dict.get(name, None)

    def setNamedItem(self, item: Attr) -> None:
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('setAttribute', item.name, item.value)
        self._dict[item.name] = item
        item._owner = self._owner

    def removeNamedItem(self, item: Attr) -> Optional[Attr]:
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('removeAttribute', item.name)
        removed_item = self._dict.pop(item.name, None)
        if removed_item:
            removed_item._owner = self._owner
        return removed_item

    def item(self, index: int) -> Optional[Attr]:
        if 0 <= index < len(self):
            return self._dict[tuple(self._dict.keys())[index]]
        return None

    def toString(self) -> str:
        return ' '.join(attr.html for attr in self._dict.values())


class ElementParser(FragmentParser):
    def __init__(self, *args: Any, default_class: type = None,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.default_class = Element


class HTMLElementParser(ElementParser):
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
    def __new__(cls: type, name: str, bases: Tuple[type],
                namespace: Dict[str, Any], **kwargs: Any) -> type:
        for attr in namespace.get('_special_attr_string', []):
            namespace[attr] = _string_properties(attr)
        for attr in namespace.get('_special_attr_boolean', []):
            namespace[attr] = _boolean_properties(attr)
        new_cls = super().__new__(cls, name, bases, dict(namespace))
        return new_cls


class Element(Node, EventTarget, ParentNode, NonDocumentTypeChildNode,
              ChildNode, metaclass=ElementMeta):
    nodeType = Node.ELEMENT_NODE
    nodeValue = None
    _parser_class = ElementParser  # type: Type[ElementParser]
    _elements = WeakSet()  # type: WeakSet[Node]
    _elements_with_id = WeakValueDictionary()  # type: MutableMapping
    _should_escape_text = True
    _special_attr_string = ['id']
    _special_attr_boolean = []  # type: List[str]

    def __init__(self, tag: str='', parent: Node = None,
                 _registered: bool = True, **kwargs: Any) -> None:
        self._registered = _registered
        self.tag = tag
        self._elements.add(self)  # used to suport custom elements
        self.attributes = NamedNodeMap(self)
        self.classList = DOMTokenList(self)
        super().__init__(parent=parent)

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

    def _parse_html(self, html: str) -> DocumentFragment:
        parser = self._parser_class()
        parser.feed(html)
        return parser.root

    def _get_inner_html(self) -> str:
        return ''.join(child.html for child in self._children)

    def _set_inner_html(self, html: str) -> None:
        self._empty()
        self._append_child(self._parse_html(html))

    @property
    def innerHTML(self) -> str:
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html: str) -> None:
        self._set_inner_html(html)

    @property
    def end_tag(self) -> str:
        return '</{}>'.format(self.tag)

    @property
    def html(self) -> str:
        return self.start_tag + self.innerHTML + self.end_tag

    def insertAdjacentHTML(self, position: str, html: str) -> None:
        '''Parse ``html`` to DOM and insert to ``position``. ``position`` is a
        case-insensive string, and must be one of "beforeBegin", "afterBegin",
        "beforeEnd", or "afterEnd".
        '''
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
        return self.html

    @property
    def nodeName(self) -> str:  # type: ignore
        return self.tag.upper()

    @property
    def tagName(self) -> str:
        return self.tag.upper()

    @property
    def localName(self) -> str:
        return self.tag.lower()

    def getAttribute(self, attr: str) -> _AttrValueType:
        if attr == 'class':
            if self.classList:
                return self.classList.toString()
            return None
        attr_node = self.getAttributeNode(attr)
        if attr_node is None:
            return None
        return attr_node.value

    def getAttributeNode(self, attr: str) -> Optional[Attr]:
        return self.attributes.getNamedItem(attr)

    def hasAttribute(self, attr: str) -> bool:
        if attr == 'class':
            return bool(self.classList)
        return attr in self.attributes

    def hasAttributes(self) -> bool:
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
        self._set_attribute(attr, value)

    def setAttributeNode(self, attr: Attr) -> None:
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
        self._remove_attribute(attr)

    def removeAttributeNode(self, attr: Attr) -> Optional[Attr]:
        return self.attributes.removeNamedItem(attr)

    def getElementsBy(self, cond: Callable[['Element'], bool]) -> NodeList:
        '''Return list of child nodes which matches ``cond``.
        ``cond`` must be a function which gets a single argument ``node``,
        and returns bool. If the node matches requested condition, ``cond``
        should return True.
        This searches all child nodes recursively.
        '''
        elements = []
        for child in self.children:
            if cond(child):
                elements.append(child)
            elements.extend(child.getElementsBy(cond))
        return NodeList(elements)

    def getElementsByTagName(self, tag: str) -> NodeList:
        _tag = tag.upper()
        return self.getElementsBy(lambda n: getattr(n, 'tagName') == _tag)

    def getElementsByClassName(self, class_name: str) -> NodeList:
        return self.getElementsBy(
            lambda node: class_name in getattr(node, 'classList'))


class HTMLElement(Element):
    _special_attr_string = ['title', 'type']
    _special_attr_boolean = ['hidden']
    _parser_class = HTMLElementParser  # type: Type[ElementParser]

    def __init__(self, *args: Any, style: str=None, **kwargs: Any) -> None:
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
        return super().end_tag

    @property
    def style(self) -> CSSStyleDeclaration:
        return self._style

    @style.setter
    def style(self, style: _AttrValueType) -> None:
        if isinstance(style, str):
            self._style._parse_str(style)
        elif style is None:
            self._style._parse_str('')
        elif isinstance(style, CSSStyleDeclaration):
            self._style._owner = None
            style._owner = self  # type: ignore
            self._style = style
            self._style.update()  # type: ignore
        else:
            raise TypeError('Invalid type for style: {}'.format(type(style)))

    @property
    def draggable(self) -> Union[bool, str]:
        if not self.hasAttribute('draggable'):
            return False
        return self.getAttribute('draggable')  # type: ignore

    @draggable.setter
    def draggable(self, val: Union[bool, str]) -> None:
        if val is False:
            self.removeAttribute('draggable')
        else:
            self.setAttribute('draggable', val)

    def getAttribute(self, attr: str) -> _AttrValueType:
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


class FormControlMixin:
    @property
    def parentNode(self) -> Optional[Node]: ...  # for type check

    def __init__(self, *args: Any,
                 form: Optional[Union[str, int, 'HTMLFormElement']] = None,
                 **kwargs: Any) -> None:
        self._form = None
        super().__init__(*args, **kwargs)  # type: ignore
        from wdom.document import getElementById
        if isinstance(form, (str, int)):
            form = getElementById(form)
        if isinstance(form, HTMLFormElement):
            self._form = form
        elif form is not None:
            raise TypeError(
                '"form" attribute must be an HTMLFormElement or id of'
                'HTMLFormElement in the same document.'
            )

    @property
    def form(self) -> Optional['HTMLFormElement']:
        if self._form:
            return self._form
        parent = self.parentNode
        while parent:
            if isinstance(parent, HTMLFormElement):
                return parent
            else:
                parent = parent.parentNode
        return None


class HTMLAnchorElement(HTMLElement):
    _special_attr_string = ['href', 'name', 'rel', 'src', 'target']


class HTMLButtonElement(HTMLElement):
    _special_attr_string = ['name', 'value']
    _special_attr_boolean = ['disabled']


class HTMLFormElement(HTMLElement):
    _special_attr_string = ['name']


class HTMLIFrameElement(HTMLElement):
    _special_attr_string = ['height', 'name', 'src', 'target', 'width']


class HTMLInputElement(HTMLElement, FormControlMixin):
    _special_attr_string = ['height', 'name', 'src', 'value', 'width']
    _special_attr_boolean = ['checked', 'disabled', 'multiple', 'readonly',
                             'required']

    def on_event_pre(self, e: Event) -> None:
        super().on_event_pre(e)
        if e.type in ('input', 'change'):
            # Update user inputs
            if self.type.lower() == 'checkbox':
                self._set_attribute('checked', e.currentTarget.get('checked'))
            elif self.type.lower() == 'radio':
                self._set_attribute('checked', e.currentTarget.get('checked'))
                for other in self._radio_group:
                    if other is not self:
                        other._remove_attribute('checked')
            else:
                self._set_attribute('value', e.currentTarget.get('value'))

    @property
    def defaultChecked(self) -> bool:
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
        return self.getAttribute('defaultValue')

    @defaultValue.setter
    def defaultValue(self, value: str) -> None:
        self.setAttribute('defaultValue', value)
        self.value = value

    @property
    def _radio_group(self) -> NodeList:
        if self.type.lower() == 'radio' and self.form and self.name:
            return NodeList([elm for elm in self.form
                             if elm.tagName == 'INPUT' and
                             elm.type.lower() == 'radio' and
                             elm.name == self.name])
        return NodeList([])


class HTMLLabelElement(HTMLElement, FormControlMixin):
    @property
    def htmlFor(self) -> _AttrValueType:
        return self.getAttribute('for')

    @htmlFor.setter
    def htmlFor(self, value: str) -> None:
        self.setAttribute('for', value)

    @property
    def control(self) -> Optional[HTMLElement]:
        id = self.getAttribute('for')
        if id:
            if self.ownerDocument:
                return self.ownerDocument.getElementById(id)
            elif isinstance(id, (str, int)):
                from wdom.document import getElementById
                return getElementById(id)
            else:
                raise TypeError
        return None


class HTMLOptGroupElement(HTMLElement, FormControlMixin):
    _special_attr_string = ['label']
    _special_attr_boolean = ['disabled']


class HTMLOptionElement(HTMLElement, FormControlMixin):
    _special_attr_string = ['label', 'value']
    _special_attr_boolean = ['defaultSelected', 'disabled', 'selected']


class HTMLScriptElement(HTMLElement):
    _special_attr_string = ['charset', 'src']
    _special_attr_boolean = ['async', 'defer']
    _should_escape_text = False


class HTMLSelectElement(HTMLElement, FormControlMixin):
    _special_attr_string = ['name', 'size', 'value']
    _special_attr_boolean = ['disabled', 'multiple', 'required']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._selected_options = []  # type: List[str]
        super().__init__(*args, **kwargs)

    def on_event_pre(self, e: Event) -> None:
        super().on_event_pre(e)
        if e.type in ('input', 'change'):
            self._set_attribute('value', e.currentTarget.get('value'))
            _selected = e.currentTarget.get('selectedOptions', [])
            self._selected_options.clear()
            for opt in self.options:
                if opt.rimo_id in _selected:
                    self._selected_options.append(opt)
                    opt._set_attribute('selected', True)
                else:
                    opt._remove_attribute('selected')

    @property
    def length(self) -> int:
        return len(self.options)

    @property
    def options(self) -> NodeList:
        return self.getElementsByTagName('option')

    @property
    def selectedOptions(self) -> NodeList:
        return NodeList(list(opt for opt in self.options if opt.selected))


class HTMLStyleElement(HTMLElement):
    _special_attr_boolean = ['disabled', 'scoped']
    _should_escape_text = False


class HTMLTextAreaElement(HTMLElement, FormControlMixin):
    _special_attr_string = ['height', 'name', 'src', 'value', 'width']
    _special_attr_boolean = ['disabled']
    defaultValue = HTMLElement.textContent

    def on_event_pre(self, e: Event) -> None:
        super().on_event_pre(e)
        if e.type in ('input', 'change'):
            # Update user inputs
            self._set_text_content(e.currentTarget.get('value') or '')
