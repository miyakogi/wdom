#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Iterable, OrderedDict
from xml.etree.ElementTree import HTML_EMPTY
import html as html_
from html.parser import HTMLParser
from typing import Union, Tuple, Callable
from weakref import WeakSet, WeakValueDictionary

from wdom.interface import NodeList, Event
from wdom.css import CSSStyleDeclaration
from wdom.node import Node, ParentNode, NonDocumentTypeChildNode, ChildNode
from wdom.node import DocumentFragment, Comment
from wdom.event import EventTarget
from wdom.webif import WebIF


class DOMTokenList:
    """List of DOM token.

    DOM token is a string which does not contain spases.
    """
    def __init__(self, owner, *args):
        self._list = list()
        self._owner = owner
        self._append(args)

    def __len__(self) -> int:
        return len(self._list)

    def __contains__(self, item: str) -> bool:
        return item in self._list

    def __iter__(self) -> str:
        for token in self._list:
            yield token

    def _validate_token(self, token: str):
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
        """Number of DOM token in this list."""
        return len(self)

    def add(self, *tokens: Tuple[str]):
        """Add new tokens to list."""
        _new_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token and token not in self:
                self._list.append(token)
                _new_tokens.append(token)
        if isinstance(self._owner, WebIF) and _new_tokens:
            self._owner.js_exec('addClass', _new_tokens)

    def remove(self, *tokens: Tuple[str]):
        """Remove tokens from list."""
        _removed_tokens = []
        for token in tokens:
            self._validate_token(token)
            if token in self:
                self._list.remove(token)
                _removed_tokens.append(token)
        if isinstance(self._owner, WebIF) and _removed_tokens:
            self._owner.js_exec('removeClass', _removed_tokens)

    def toggle(self, token: str):
        """Add or remove token to/from list.

        If token is in this list, the token will be removed. Otherwise add it
        to list.
        """
        self._validate_token(token)
        if token in self:
            self.remove(token)
        else:
            self.add(token)

    def item(self, index: int) -> str:
        """Return the token of the ``index``.

        ``index`` must be 0 or positive integer. If index is out of range,
        return None.
        """
        if 0 <= index < len(self):
            return self._list[index]
        else:
            return None

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
    def __init__(self, name: str, value=None, owner: Node = None):
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
            if isinstance(self.value, str):
                value = html_.escape(self.value)
            else:
                value = self.value
            return '{name}="{value}"'.format(name=self.name, value=value)

    @property
    def name(self) -> str:
        """Name of this attr."""
        return self._name

    @property
    def value(self) -> str:
        """Value of this attr."""
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def isId(self) -> bool:
        """Return True if this Attr is an ID node (name is ``id``)."""
        return self.name.lower() == 'id'


class NamedNodeMap:
    def __init__(self, owner):
        self._owner = owner
        self._dict = OrderedDict()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, item: str) -> bool:
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

    def getNamedItem(self, name: str) -> Attr:
        return self._dict.get(name, None)

    def setNamedItem(self, item: Attr):
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('setAttribute', item.name, item.value)
        self._dict[item.name] = item
        item._owner = self._owner

    def removeNamedItem(self, item: Attr) -> Attr:
        if not isinstance(item, Attr):
            raise TypeError('item must be an instance of Attr')
        if isinstance(self._owner, WebIF):
            self._owner.js_exec('removeAttribute', item.name)
        removed_item = self._dict.pop(item.name, None)
        if removed_item:
            removed_item._owner = self._owner
        return removed_item

    def item(self, index: int) -> Attr:
        if 0 <= index < len(self):
            return self._dict[tuple(self._dict.keys())[index]]
        else:
            return None

    def toString(self) -> str:
        return ' '.join(attr.html for attr in self._dict.values())


def _create_element(tag: str, name: str = None, base: type = None,
                    attr: dict = None):
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
        if self.elm:
            self.elm.append(elm)
        if tag not in HTML_EMPTY:
            self.elm = elm

    def handle_endtag(self, tag):
        self.elm = self.elm.parentNode

    def handle_data(self, data):
        if data and self.elm:
            self.elm.append(data)

    def handle_comment(self, comment: str):
        self.elm.append(Comment(comment))


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


def _string_properties(attr) -> property:
    def getter(self) -> str:
        return self.getAttribute(attr) or ''

    def setter(self, value: str):
        self.setAttribute(attr, str(value))

    def deleter(self):
        self.removeAttribute(attr)

    return property(getter, setter, deleter, _str_attr_doc.format(attr=attr))


def _boolean_properties(attr) -> property:
    def getter(self: Node) -> bool:
        return bool(self.getAttribute(attr))

    def setter(self: Node, value: bool):
        if value:
            self.setAttribute(attr, True)
        else:
            self.removeAttribute(attr)

    def deleter(self):
        self.removeAttribute(attr)

    return property(getter, setter, deleter, _bool_attr_doc.format(attr=attr))


class ElementMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
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
    _parser_default_class = None
    _elements = WeakSet()
    _elements_with_id = WeakValueDictionary()
    _should_escape_text = True
    _special_attr_string = ['id']
    _special_attr_boolean = []

    def __init__(self, tag: str='', parent: Node = None,
                 _registered: bool = True, **kwargs):
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
        parser = Parser(default_class=self._parser_default_class)
        parser.feed(html)
        return parser.root

    def _get_inner_html(self) -> str:
        return ''.join(child.html for child in self._children)

    def _set_inner_html(self, html: str):
        self._empty()
        self._append_child(self._parse_html(html))

    @property
    def innerHTML(self) -> str:
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html: str):
        self._set_inner_html(html)

    @property
    def end_tag(self) -> str:
        return '</{}>'.format(self.tag)

    @property
    def html(self) -> str:
        return self.start_tag + self.innerHTML + self.end_tag

    def insertAdjacentHTML(self, position: str, html: str):
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
    def nodeName(self) -> str:
        return self.tag.upper()

    @property
    def tagName(self) -> str:
        return self.tag.upper()

    @property
    def localName(self) -> str:
        return self.tag.lower()

    def getAttribute(self, attr: str) -> str:
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

    def getAttributeNode(self, attr: str) -> Attr:
        return self.attributes.getNamedItem(attr)

    def hasAttribute(self, attr: str) -> bool:
        if attr == 'class':
            return bool(self.classList)
        else:
            return attr in self.attributes

    def hasAttributes(self) -> bool:
        return bool(self.attributes) or bool(self.classList)

    def _set_attribute(self, attr: str, value: Union[str, bool]):
        if attr == 'class':
            self.classList = DOMTokenList(self, value)
        else:
            if attr == 'id':
                if 'id' in self.attributes:
                    # remove old reference to self
                    self._elements_with_id.pop(self.id, None)
                # register this elements with new id
                self._elements_with_id[value] = self
            new_attr_node = Attr(attr, value)
            self.setAttributeNode(new_attr_node)

    def setAttribute(self, attr: str, value: Union[str, bool]):
        self._set_attribute(attr, value)

    def setAttributeNode(self, attr: Attr):
        self.attributes.setNamedItem(attr)

    def _remove_attribute(self, attr: str):
        if attr == 'class':
            self.classList = DOMTokenList(self)
        else:
            if attr == 'id':
                self._elements_with_id.pop(self.id, None)
            _attr = self.getAttributeNode(attr)
            if _attr:
                self.attributes.removeNamedItem(_attr)

    def removeAttribute(self, attr: str):
        self._remove_attribute(attr)

    def removeAttributeNode(self, attr: Attr) -> Attr:
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

    def getElementsByTagName(self, tag: str):
        _tag = tag.upper()
        return self.getElementsBy(lambda n: getattr(n, 'tagName') == _tag)

    def getElementsByClassName(self, class_name: str):
        return self.getElementsBy(
            lambda node: class_name in getattr(node, 'classList'))


class HTMLElement(Element):
    _special_attr_string = ['title', 'type']
    _special_attr_boolean = ['draggable', 'hidden']

    def __init__(self, *args, style: str=None, **kwargs):
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

    @property
    def style(self) -> CSSStyleDeclaration:
        return self._style

    @style.setter
    def style(self, style: str):
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

    def getAttribute(self, attr: str) -> str:
        if attr == 'style':
            # if style is neither None nor empty, return None
            # otherwise, return style.cssText
            if self.style:
                return self.style.cssText
            else:
                return None
        else:
            return super().getAttribute(attr)

    def _set_attribute(self, attr: str, value: str):
        if attr == 'style':
            self.style = value
        else:
            super()._set_attribute(attr, value)

    def _remove_attribute(self, attr: str):
        if attr == 'style':
            self.style = None
        else:
            super()._remove_attribute(attr)


class FormControlMixin:
    def __init__(self, *args, form=None, **kwargs):
        self._form = None
        super().__init__(*args, **kwargs)
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
    def form(self) -> HTMLElement:
        if self._form:
            return self._form
        else:
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


class HTMLInputElement(FormControlMixin, HTMLElement):
    _special_attr_string = ['height', 'name', 'src', 'value', 'width']
    _special_attr_boolean = ['checked', 'disabled', 'multiple', 'readonly',
                             'required']

    def on_event_pre(self, e: Event):
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
    def defaultChecked(self, value: bool):
        if value:
            self.setAttribute('defaultChecked', True)
            self.checked = True
        else:
            self.removeAttribute('defaultChecked')
            self.checked = False

    @property
    def defaultValue(self) -> str:
        return self.getAttribute('defaultValue')

    @defaultValue.setter
    def defaultValue(self, value: str):
        self.setAttribute('defaultValue', value)
        self.value = value

    @property
    def _radio_group(self) -> NodeList:
        if self.type.lower() == 'radio' and self.form and self.name:
            return NodeList([elm for elm in self.form
                             if elm.tagName == 'INPUT' and
                             elm.type.lower() == 'radio' and
                             elm.name == self.name])
        else:
            return NodeList([])


class HTMLLabelElement(HTMLElement, FormControlMixin):
    @property
    def htmlFor(self) -> str:
        return self.getAttribute('for')

    @htmlFor.setter
    def htmlFor(self, value: str):
        self.setAttribute('for', value)

    @property
    def control(self) -> HTMLElement:
        id = self.getAttribute('for')
        if id:
            if self.ownerDocument:
                return self.ownerDocument.getElementById(id)
            else:
                from wdom.document import getElementById
                return getElementById(id)


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

    def __init__(self, *args, **kwargs):
        self._selected_options = []
        super().__init__(*args, **kwargs)

    def on_event_pre(self, e: Event):
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

    def on_event_pre(self, e: Event):
        super().on_event_pre(e)
        if e.type in ('input', 'change'):
            # Update user inputs
            self._set_text_content(e.currentTarget.get('value') or '')
