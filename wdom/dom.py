#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from collections import ChainMap, Iterable
from functools import partial
import html
from xml.etree.ElementTree import HTML_EMPTY
from asyncio import coroutine, ensure_future, iscoroutine, Future
from inspect import iscoroutinefunction
from typing import List, Callable, Union, Tuple, Optional

logger = logging.getLogger(__name__)
connections = []
elements = {}


def _ensure_dom(dom: Union['Dom', str]) -> 'Dom':
    if isinstance(dom, TextNode):
        return dom
    else:
        return TextNode(str(dom))


class TextNode:
    '''Node which contains only text. When converted to html, inner text will
    be escaped, for example, ``>`` to ``&lt;``.
    '''
    def __init__(self, text, parent: 'Dom' = None):
        self._text = text
        self.parent = parent

    @property
    def html(self) -> str:
        '''return escaped expression of this node.'''
        return html.escape(self._text)

    def remove(self):
        '''Remove this node from the parent's tree.'''
        if self.parent is not None:
            self.parent.children.remove(self)
            self.parent = None

    # Properties defined in xml.dom.Node
    @property
    def parentNode(self):
        '''Return parent node.'''
        return self.parent

    @property
    def previousSibling(self):
        '''Return the previous node. If this node does not have previous node,
        return ``None``.'''
        if self.parent is None or len(self.parent) < 2:
            # does not have parent or siblings
            return None
        else:
            index = self.parent.index(self)
            if index == 0:
                return None
            else:
                return self.parent[index - 1]

    @property
    def nextSibling(self):
        '''Return the next node. If this node does not have next node, return
        ``None``.'''
        if self.parent is None or len(self.parent) < 2:
            # does not have parent or siblings
            return None
        else:
            index = self.parent.index(self)
            if index == len(self.parent) - 1:
                return None
            else:
                return self.parent[index + 1]

    @property
    def textContent(self) -> str:
        # should return escaped string??
        return self._text

    @textContent.setter
    def textContent(self, text: str):
        self._text = text


class RawHtmlNode(TextNode):
    @property
    def html(self) -> str:
        return self._text


class Dom(TextNode):
    '''DOM implementation base for python.'''
    #: Tag name of this node.
    tag = 'tag'

    def __init__(self, parent: 'Dom' = None, **kwargs):
        attrs = ChainMap(kwargs)
        if 'attrs' in kwargs:
            orig_attrs = attrs.pop('attrs')
            attrs.update(orig_attrs)

        self.children = []
        self.attrs = attrs
        self.parent = parent
        self._text = None
        # Append myself to parent
        if parent is not None:
            parent.append(self)

    def get_attrs_by_string(self, **attrs) -> str:
        attrs = self.attrs.new_child(attrs)
        tag = ''
        for k, v in attrs.items():
            tag += ' {}="{}"'.format(k, str(v))
        return tag

    def start_tag(self, **attrs) -> str:
        '''Return start tag of this node. For example,
        ``Dom('h1').start_tag()`` returns ``<h1>``.'''
        html = '<' + self.tag
        html += '>'
        return '<' + self.tag + self.get_attrs_by_string() + '>'

    def _inner_text(self) -> str:
        if self._text is not None:
            return self._text.html
        else:
            return ''

    def _inner_html(self) -> str:
        return ''.join(child.html for child in self.children)

    def end_tag(self) -> str:
        '''Return start tag of this node. For example,
        ``Dom('h1').start_tag()`` returns ``<h1>``.'''
        return '' if self.tag in HTML_EMPTY else '</' + self.tag + '>'

    @property
    def html(self) -> str:
        '''Return html expression of this node, including child nodes.'''
        html = self.start_tag()
        html += self._inner_text()
        html += self._inner_html()
        html += self.end_tag()
        return html

    def insert(self, pos: int, child: 'Dom'):
        '''Insert child node as the ``pos``-th child. If child is not an
        instance of Dom, it is converted to string and wrapped by TextNode
        before inserting it.'''
        if not isinstance(child, TextNode):
            raise TypeError('child must be type of Node: {}'.format(child))
        self.children.insert(pos, child)
        child.parent = self

    def append(self, child: 'Dom'):
        '''Append child node at the end of child nodes. If child is not an
        instance of Dom, it is converted to string and wrapped by TextNode
        before appending it.'''
        if not isinstance(child, TextNode):
            raise TypeError('child must be type of Node: {}'.format(child))
        self.children.append(child)
        child.parent = self

    def __iter__(self) -> 'Dom':
        for child in self.children:
            yield child

    def __len__(self) -> int:
        return len(self.children)

    def __contains__(self, other) -> bool:
        if other in self.children:
            return True
        if isinstance(other, Dom):
            return False
        else:
            other = str(other)
            return any(other == child._text for child in self.children if isinstance(child, TextNode))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.children[key]
        return self.attrs[key]

    def __setitem__(self, key: str, item):
        self.attrs[key] = item

    def __delitem__(self, key: str):
        del self.attrs[key]

    def __copy__(self) -> 'Dom':
        attrs = self.attrs.copy()
        clone = type(self)(**attrs)
        return clone

    def __deepcopy__(self, memo={}) -> 'Dom':
        clone = self.__copy__()
        for child in self:
            clone.append(child.__deepcopy__(memo))
        return clone

    def index(self, child: TextNode) -> int:
        return self.children.index(child)

    # Properties defined in xml.dom.Node
    @property
    def attributes(self) -> dict:
        '''Return key-value pair representation of attributes in this node. The
        order of attributes is random. Any changes to the returned object does
        not reflect to the origin node. If you want to change attribute, use
        ``setAttribute()`` instead.
        '''
        return self.attrs.copy()

    @property
    def childNodes(self) -> list:
        '''Return list of child nodes. If you want to iterate them, use
        ``iter(self)`` instead.
        '''
        return self.children

    @property
    def firstChild(self) -> 'Dom':
        '''Return first child node. If this node has no child nodes, return
        None.'''
        if self.hasChildNodes():
            return self.children[0]
        else:
            return None

    @property
    def lastChild(self) -> 'Dom':
        '''Return last child node. If this node has no child nodes, return
        None.'''
        if self.hasChildNodes():
            return self.children[-1]
        else:
            return None

    @property
    def localName(self) -> str:
        '''Return ``tagname`` of this node, in lower case.'''
        return self.tag.lower()

    def hasAttributes(self) -> bool:
        '''Return ``True`` if this node has any attributes.'''
        return bool(self.attrs)

    def hasChildNodes(self) -> bool:
        '''Return ``True`` if this node has any child nodes.'''
        return len(self.children) > 0

    def appendChild(self, newChild: 'Dom'):
        '''Append new node into the last of this child nodes.'''
        self.append(newChild)

    def removeChild(self, child: Union['Dom', str]):
        '''Remove child node from this node's content. The node is not a child
        of this node, raise ValueError.'''
        if child not in self:
            raise ValueError('No such child: {}'.format(child))
        child.remove()

    def replaceChild(self, new_child: 'Dom', old_child: 'Dom'):
        '''Replace child node with new node. The node to be replaced is not a
        child of this node, raise ValueError.'''
        if old_child not in self:
            raise ValueError('No such child: {}'.format(old_child))
        self.insert(self.index(old_child), new_child)
        old_child.remove()
        # Need to swap parent of new/old child?

    def normalize(self) -> str:
        '''Not implemented yet.'''
        raise NotImplementedError

    def cloneNode(self, deep=False) -> 'Dom':
        '''Return clone of this node. New node is not an element of any tree.
        If ``deep`` is True, child nodes are copied as well and added to new
        node.'''
        if deep:
            return self.__deepcopy__()
        else:
            return self.__copy__()

    # Properties defined in xml.dom.Element
    @property
    def tagName(self) -> str:
        '''Return ``tagname`` of this node, in upper case.'''
        return self.tag.upper()

    def getElementsByTagName(self, tag: str, recursive=True) -> List['Dom']:
        '''Return all child nodes with ``tagname``.'''
        elements = []
        for child in self:
            if isinstance(child, Dom):
                if child.tag == tag:
                    elements.append(child)
                if recursive:
                    elements += child.getElementsByTagName(tag)
        return elements

    def hasAttribute(self, attr: str) -> bool:
        return attr in self.attrs

    def getAttribute(self, attr: str) -> str:
        # TODO: need check `attr` is `class` or `style`
        try:
            return self[attr]
        except KeyError:
            return None

    def removeAttribute(self, attr: str) -> str:
        del self.attrs[attr]

    def setAttribute(self, attr: str, value: str):
        self.attrs[attr] = value

    # Javascript-like DOM API
    @property
    def textContent(self) -> str:
        '''Get inner text.'''
        text = ''.join(child.textContent for child in self.childNodes)
        return text

    @textContent.setter
    def textContent(self, text: str):
        '''Remove all inner contents of this node, and set new text.'''
        for child in tuple(self):
            child.remove()
        if text:
            self.append(_ensure_dom(text))


class ClassList:
    def __init__(self, *args):
        self.classes = []
        self.append(args)

    def append(self, *args):
        for arg in args:
            if isinstance(arg, (str, bytes)):
                for c in arg.split():
                    if c not in self.classes:
                        self.classes.append(c)
            elif isinstance(arg, TextNode):
                raise TypeError(
                    'class must be str, bytes, or Iterable of them,'
                    ' not {}'.format(type(arg)))
            elif isinstance(arg, Iterable):
                for c in arg:
                    self.append(c)
            elif arg is None:
                pass
            else:
                raise TypeError(
                    'class must be str, bytes, or Iterable of them,'
                    ' not {}'.format(type(arg)))

    def remove(self, item):
        self.classes.remove(item)

    def to_string(self) -> str:
        return ' '.join(self.classes)

    def reverse(self) -> None:
        '''Reverse order of classes *in place*.'''
        self.classes.reverse()

    def __contains__(self, item) -> bool:
        return item in self.classes

    def __bool__(self) -> bool:
        return bool(self.classes)

    def __len__(self) -> int:
        return len(self.classes)

    def __iter__(self) -> str:
        for c in self.classes:
            yield c


class HtmlDomMeta(type):
    '''Meta class to set default class variable of HtmlDom'''
    def __prepare__(name, bases, **kwargs) -> dict:
        return {'inherit_class': True}


class HtmlDom(Dom, metaclass=HtmlDomMeta):
    '''Add support for some special attrs(class, type, is, hidden)'''
    tag = 'html-tag'
    #: str and list of strs are acceptale.
    class_ = ''
    inherit_class = True
    #: use for <input> tag's type
    type_ = ''
    #: custom element which extends built-in tag (like <table is="your-tag">)
    is_ = ''

    @classmethod
    def get_class_list(cls) -> ClassList:
        l = []
        l.append(ClassList(cls.class_))
        if cls.inherit_class:
            for base_cls in cls.__bases__:
                if issubclass(base_cls, HtmlDom):
                    l.append(base_cls.get_class_list())
        # Reverse order so that parent's class comes to front
        l.reverse()
        return ClassList(l)

    def __init__(self, class_=None, hidden:bool=False, **kwargs):
        self.class_list = ClassList(class_)
        self.hidden = hidden
        if class_:
            self.class_list.append(class_)
        super().__init__(**kwargs)

    def get_attrs_by_string(self, **attrs) -> str:
        attrs = self.attrs.new_child(attrs)
        classes = self.__class__.get_class_list()
        classes.append(self.class_list)
        if classes:
            attrs['class'] = ' '.join(classes)
        if self.type:
            attrs['type'] = self.type
        attrs_str = super().get_attrs_by_string(**attrs)
        if self.hidden:
            attrs_str += ' hidden'
        return attrs_str

    def __getitem__(self, attr: str):
        if attr == 'class':
            return self.class_list.to_string()
        else:
            return super().__getitem__(attr)

    def __setitem__(self, attr: str, val):
        if attr == 'class':
            self.class_list = ClassList(val)
        else:
            super().__setitem__(attr, val)

    def __copy__(self) -> 'HtmlDom':
        clone = super().__copy__()
        for c in self.class_list:
            clone.addClass(c)
        clone.hidden = self.hidden
        return clone

    def addClass(self, class_: str):
        self.class_list.append(class_)

    def hasClass(self, class_: str):
        return class_ in self.class_list

    def hasClasses(self):
        return len(self.class_list) > 0

    def removeClass(self, class_: str):
        try:
            self.class_list.remove(class_)
        except ValueError:
            if class_ in self.__class__.get_class_list():
                logger.warn(
                    'tried to remove class-level class: '
                    '{}'.format(class_)
                )
            else:
                logger.warn(
                    'tried to remove non-existing class: {}'.format(class_)
                )

    def show(self):
        self.hidden = False

    def hide(self):
        self.hidden = True

    @property
    def type(self) -> str:
        return self.attrs.get('type', self.__class__.type_)

    @type.setter
    def type(self, val:str) -> None:
        self.attrs['type'] = val


class PyNode(HtmlDom):
    tag = 'py-node'

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', str(id(self)))
        super().__init__(**kwargs)

    def get_attrs_by_string(self, **attrs) -> str:
        attrs_str = super().get_attrs_by_string(**attrs)
        attrs_str += ' id="{}"'.format(self.id)
        return attrs_str


class EventListener:
    '''Class to wrap an event listener. Acceptable listeners are function,
    coroutine, and coroutine-function. If ``apply_data`` is True, ``data`` is
    applied as a keyword argument of ``data`` when the registered event is
    triggered.'''
    # Should support generator?
    def __init__(self, listener: Callable, apply_data: bool = True):
        self.listener = listener
        self.apply_data = apply_data

        if iscoroutine(self.listener):
            self.action = partial(ensure_future, self.listener)
        elif iscoroutinefunction(self.listener):
            self.action = self.wrap_coro_func(self.listener)
        else:
            self.action = self.listener

    def wrap_coro_func(self, coro) -> Callable:
        def wrapper(*args, **kwargs):
            nonlocal coro
            ensure_future(coro(*args, **kwargs))
        return wrapper

    def __call__(self, data):
        if self.apply_data:
            self.action(data=data)
        else:
            self.action()


class Node(PyNode):
    tag = 'node'

    def __init__(self, *args, **kwargs):
        self.listeners = dict()
        super().__init__(*args, **kwargs)
        elements[self.id] = self

    def get_attrs_by_string(self, **attrs) -> str:
        attrs_str = super().get_attrs_by_string(**attrs)
        for event in self.listeners:
            attrs_str += ' on{event}="W.on{event}(this);"'.format(event=event)
        return attrs_str

    @property
    def connected(self) -> bool:
        '''This instance has any connection on browser or not.'''
        return any(connections)

    @coroutine
    def on_message(self, msg: dict):
        '''Coroutine when webscoket get message to this instance is called.'''
        logger.debug('WS MSG  {tag}: {msg}'.format(tag=self.tag, msg=msg))

        event = msg.get('event', False)
        if event:
            data = msg.get('data')
            for listener in self.listeners.get(event, []):
                listener(data=data)

    def addEventListener(self, event: str, listener: Callable):
        '''Add event listener to this instance. ``event`` is a string which
        determines the event type when the new listener called.'''
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(EventListener(listener))

    def removeEventListener(self, event: str, listener: Callable):
        listeners = self.listeners[event]
        for l in listeners:
            if l.listener == listener:
                listeners.remove(l)
                break
        if len(listeners) == 0:
            del self.listeners[event]

    def js_exec(self, method: str, **kwargs) -> Optional[Future]:
        '''Execute ``method`` in the related node on browser via web socket
        connection. Other keyword arguments are passed to ``params`` attribute.
        If this node is not in document tree (namely, this node does not have
        parent node), the ``method`` is not executed.
        '''
        if self.parent is not None:
            return ensure_future(
                self.ws_send(dict(method=method, params=kwargs))
            )

    @coroutine
    def ws_send(self, obj):
        '''Send message to the related node on browser, with ``tagname`` and
        ``pyg_id`` which specifies relation between python object and element
        on browser. The message is serialized by JSON object and send via
        WebSocket connection.'''
        obj['id'] = self.id
        obj['tag'] = self.tag
        msg = json.dumps(obj)
        for conn in connections:
            conn.write_message(msg)

    def append(self, child):
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.'''
        super().append(child)
        self.js_exec('append', html=self[-1].html)

    def insert(self, pos: int, new_child):
        '''Insert child node at the specified ``position``. The same operation
        will be done also in the related node on browser, if exists.'''
        super().insert(pos, new_child)
        self.js_exec('insert', index=pos, html=self[pos].html)

    def remove(self, *args, **kwargs):
        '''Remove this node and this child nodes from parent's DOM tree.'''
        fut = self.js_exec('remove')
        fut.add_done_callback(self._remove_callback)

    def _remove_callback(self, *args, **kwargs):
        super().remove()

    def removeAttribute(self, attr: str) -> str:
        super().removeAttribute(attr)
        self.js_exec('removeAttribute', attr=attr)

    def setAttribute(self, attr: str, value: str, **kwargs):
        super().setAttribute(attr, value)
        self.js_exec('setAttribute', attr=attr, value=value)

    def appendChild(self, new_child: 'Node'):
        '''Append new node into the last of this child nodes.'''
        self.append(new_child)

    def removeChild(self, child: 'Node'):
        '''Remove child node from this node's content. The node is not a child
        of this node, raise ValueError.'''
        super().removeChild(child)
        self.js_exec('removeChild', id=child.id)

    def replaceChild(self, new_child: 'Node', old_child: 'Node'):
        '''Replace child node with new node. The node to be replaced is not a
        child of this node, raise ValueError.'''
        super().replaceChild(new_child, old_child)
        self.js_exec('replaceChild', id=old_child.id, html=new_child.html)

    @property
    def textContent(self) -> str:
        return PyNode.textContent.fget(self)

    @textContent.setter
    def textContent(self, text: str):
        PyNode.textContent.fset(self, text)
        self.js_exec(method='textContent', text=text)

    def show(self, **kwargs):
        self.js_exec('show')
        super().show()

    def hide(self, **kwargs):
        self.js_exec('hide')
        super().hide()

    def addClass(self, cls: str, **kwargs):
        if cls and cls not in self.class_list:
            self.js_exec('addClass', **{'class': cls})
            super().addClass(cls)

    def removeClass(self, cls: str, **kwargs):
        if cls and  cls in self.class_list:
            self.js_exec('removeClass', **{'class': cls})
            super().removeClass(cls)


def NewNodeClass(class_name: str, tag: str=None, bases: Tuple[type]=(Node, ),
                 **attrs) -> type:
    if tag is None:
        tag = class_name.lower()
    if type(bases) is not tuple:
        if isinstance(bases, Iterable):
            bases = tuple(bases)
        elif isinstance(bases, type):
            bases = (bases, )
        else:
            TypeError('Invalid base class: {}'.format(str(bases)))
    cls = type(class_name, bases, attrs)
    cls.tag = tag
    return cls


class Input(Node):
    tag = 'input'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.addEventListener('change', self._update)
        self.addEventListener('input', self._update)

    def _update(self, data) -> None:
        if self.type in ('checkbox', 'radio'):
            self.checked = data.get('checked')
        else:
            self.value = data.get('value')

    @property
    def checked(self) -> bool:
        return self.attrs.get('checked')

    @checked.setter
    def checked(self, value: bool) -> None:
        self.attrs['checked'] = value

    @property
    def value(self) -> str:
        return self.attrs.get('value')

    @value.setter
    def value(self, value: str) -> None:
        self.attrs['value'] = value


class TextArea(Input):
    tag = 'textarea'

    @property
    def value(self) -> str:
        return self.textContent

    @value.setter
    def value(self, value: str) -> None:
        self.textContent = value


class CheckBox(Input):
    type_ = 'checkbox'


class TextInput(Input):
    type_ = 'text'


class Button(Node):
    tag = 'button'


Div = NewNodeClass('Div')
Span = NewNodeClass('Span')

# Typography
H1 = NewNodeClass('H1')
H2 = NewNodeClass('H2')
H3 = NewNodeClass('H3')
H4 = NewNodeClass('H4')
H5 = NewNodeClass('H5')
H6 = NewNodeClass('H6')

P = NewNodeClass('P')
A = NewNodeClass('A')
Strong = NewNodeClass('Strong')
Em = NewNodeClass('Em')
U = NewNodeClass('U')
Br = NewNodeClass('Br')
Hr = NewNodeClass('Hr')

Cite = NewNodeClass('Cite')
Code = NewNodeClass('Code')
Pre = NewNodeClass('Pre')

Img = NewNodeClass('Img')

# table tags
Table = NewNodeClass('Table')
Thead = NewNodeClass('Thead')
Tbody = NewNodeClass('Tbody')
Tfoot = NewNodeClass('Tfoot')
Th = NewNodeClass('Th')
Tr = NewNodeClass('Tr')
Td = NewNodeClass('Td')

# List tags
Ol = NewNodeClass('Ol')
Ul = NewNodeClass('Ul')
Li = NewNodeClass('Li')

# Definition-list tags
Dl = NewNodeClass('Dl')
Dt = NewNodeClass('Dt')
Dd = NewNodeClass('Dd')

# Form tags
Form = NewNodeClass('Form')
Label = NewNodeClass('Label')
Option = NewNodeClass('Option')
Select = NewNodeClass('Select')

# Building blocks
Container = Div
Wrapper = Div
Row = Div
