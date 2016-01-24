#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from collections import Iterable
from functools import partial
from asyncio import coroutine, ensure_future, iscoroutine, Future
from inspect import iscoroutinefunction
from typing import Callable, Tuple, Optional, Union

from .node import Node, HTMLElement, Text, DOMTokenList

logger = logging.getLogger(__name__)
connections = []
elements = {}


class RawHtmlNode(Text):
    @property
    def html(self) -> str:
        return self._text


class HtmlMeta(type):
    '''Meta class to set default class variable of HtmlDom'''
    def __prepare__(name, bases, **kwargs) -> dict:
        return {'inherit_class': True}


class Html(HTMLElement, metaclass=HtmlMeta):
    '''Add support for some special attrs(class, type, is, hidden)'''
    tag = 'tag'
    #: str and list of strs are acceptale.
    class_ = ''
    inherit_class = True
    #: use for <input> tag's type
    type_ = ''
    #: custom element which extends built-in tag (like <table is="your-tag">)
    is_ = ''

    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', None)
        if attrs:
            kwargs.update(attrs)
        if self.type_ and 'type' not in kwargs:
            kwargs['type'] = self.type_
        super().__init__(self.tag, *args, **kwargs)

    @classmethod
    def get_class_list(cls) -> DOMTokenList:
        l = []
        l.append(DOMTokenList(cls.class_))
        if cls.inherit_class:
            for base_cls in cls.__bases__:
                if issubclass(base_cls, Html):
                    l.append(base_cls.get_class_list())
        # Reverse order so that parent's class comes to front
        l.reverse()
        return DOMTokenList(l)

    def append(self, child:Node):
        self.appendChild(child)

    def insert(self, pos:int, child:Node):
        if isinstance(child, (str, bytes)):
            child = Text(child)
        if 0 <= pos < self.length:
            self.insertBefore(child, self.childNodes[pos])
        elif pos == self.length:
            self.appendChild(child)

    def __getitem__(self, attr: Union[str, int]):
        if isinstance(attr, int):
            return self.childNodes[attr]
        else:
            return self.getAttribute(attr)

    def __setitem__(self, attr: str, val):
        self.setAttribute(attr, val)

    def __delitem__(self, attr: str):
        self.removeAttribute(attr)

    def __copy__(self) -> 'Html':
        clone = super().__copy__()
        for c in self.classList:
            clone.addClass(c)
        return clone

    def getAttribute(self, attr:str):
        if attr == 'class':
            cls = self.get_class_list()
            cls.append(self.classList)
            if cls:
                return cls.to_string()
            else:
                return None
        else:
            return super().getAttribute(attr)

    def addClass(self, class_: str):
        self.classList.append(class_)

    def hasClass(self, class_: str):
        return class_ in self.classList

    def hasClasses(self):
        return len(self.classList) > 0

    def removeClass(self, class_: str):
        if class_ not in self.classList:
            if class_ in self.__class__.get_class_list():
                logger.warn(
                    'tried to remove class-level class: '
                    '{}'.format(class_)
                )
            else:
                logger.warn(
                    'tried to remove non-existing class: {}'.format(class_)
                )
        else:
            self.classList.remove(class_)

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


class PyNode(Html):
    tag = 'py-node'

    def __init__(self, **kwargs):
        self._id = kwargs.pop('id', str(id(self)))
        super().__init__(**kwargs)

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id:str):
        self._id = id

    def get_attrs_by_string(self) -> str:
        return ' '.join((super().get_attrs_by_string(),
                         'id="{}"'.format(self.id))).strip()


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
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.'''
        super().appendChild(new_child)
        self.js_exec('append', html=self[-1].html)

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
        if cls and cls not in self.classList:
            self.js_exec('addClass', **{'class': cls})
            super().addClass(cls)

    def removeClass(self, cls: str, **kwargs):
        if cls and  cls in self.classList:
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

