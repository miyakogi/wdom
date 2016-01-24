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
# connections = []
elements = {}


class RawHtml(Text):
    @property
    def html(self) -> str:
        return self._value

    @property
    def textContent(self) -> str:
        return self._value

    @textContent.setter
    def textContent(self, value:str):
        self._value = value


class TagBaseMeta(type):
    '''Meta class to set default class variable of HtmlDom'''
    def __prepare__(name, bases, **kwargs) -> dict:
        return {'inherit_class': True}


class TagBase(HTMLElement, metaclass=TagBaseMeta):
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
                if issubclass(base_cls, TagBase):
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

    def __copy__(self) -> 'TagBase':
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
        return self.getAttribute('type') or self.type_

    @type.setter
    def type(self, val:str) -> None:
        self.setAttribute('type', val)


class PyNode(TagBase):
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


class Tag(PyNode):
    tag = 'node'

    def __init__(self, *args, parent=None, **kwargs):
        self.listeners = dict()
        super().__init__(*args, **kwargs)
        elements[self.id] = self
        if parent is not None:
            parent.appendChild(self)

    def get_attrs_by_string(self) -> str:
        attrs_str = super().get_attrs_by_string()
        for event in self.listeners:
            attrs_str += ' on{event}="W.on{event}(this);"'.format(event=event)
        return attrs_str

    @property
    def connected(self) -> bool:
        '''This instance has any connection on browser or not.'''
        return self.ownerDocument is not None and any(self.ownerDocument.connections)

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
        for conn in self.ownerDocument.connections:
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

    def appendChild(self, child: 'Tag'):
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.
        '''
        super().appendChild(child)
        self.js_exec('append', html=self[-1].html)

    def insertBefore(self, child: 'Tag', ref_node: 'Tag'):
        super().insertBefore(child, ref_node)
        self.js_exec('insertBefore', html=child.html, id=ref_node.id)

    def removeChild(self, child: 'Tag'):
        '''Remove child node from this node's content. The node is not a child
        of this node, raise ValueError.'''
        super().removeChild(child)
        if isinstance(child, Tag):
            self.js_exec('removeChild', id=child.id)

    @property
    def textContent(self) -> str:
        return PyNode.textContent.fget(self)

    @textContent.setter
    def textContent(self, text: str):
        PyNode.textContent.fset(self, text)
        self.js_exec(method='textContent', text=text)

    def show(self, **kwargs):
        self.js_exec('show')
        self.attributes['hidden'] = False

    def hide(self, **kwargs):
        self.js_exec('hide')
        self.attributes['hidden'] = True

    def addClass(self, cls: str, **kwargs):
        if cls and cls not in self.classList:
            self.js_exec('addClass', **{'class': cls})
            super().addClass(cls)

    def removeClass(self, cls: str, **kwargs):
        if cls and  cls in self.classList:
            self.js_exec('removeClass', **{'class': cls})
            super().removeClass(cls)


def NewTagClass(class_name: str, tag: str=None, bases: Tuple[type]=(Tag, ),
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


class Input(Tag):
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
        return self.getAttribute('checked') or False

    @checked.setter
    def checked(self, value: bool):
        self.setAttribute('checked', value)

    @property
    def value(self) -> str:
        return self.getAttribute('value') or ''

    @value.setter
    def value(self, value: str):
        self.setAttribute('value', value)


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


class Button(Tag):
    tag = 'button'


class Script(Tag):
    tag = 'script'

    def __init__(self, *args, type='text/javascript', src=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('type', type)
        if src is not None:
            self.setAttribute('src', src)


Html = NewTagClass('Html')
Body = NewTagClass('Body')
Meta = NewTagClass('Meta')
Head = NewTagClass('Head')
Link = NewTagClass('Link')
Title = NewTagClass('Title')

Div = NewTagClass('Div')
Span = NewTagClass('Span')

# Typography
H1 = NewTagClass('H1')
H2 = NewTagClass('H2')
H3 = NewTagClass('H3')
H4 = NewTagClass('H4')
H5 = NewTagClass('H5')
H6 = NewTagClass('H6')

P = NewTagClass('P')
A = NewTagClass('A')
Strong = NewTagClass('Strong')
Em = NewTagClass('Em')
U = NewTagClass('U')
Br = NewTagClass('Br')
Hr = NewTagClass('Hr')

Cite = NewTagClass('Cite')
Code = NewTagClass('Code')
Pre = NewTagClass('Pre')

Img = NewTagClass('Img')

# table tags
Table = NewTagClass('Table')
Thead = NewTagClass('Thead')
Tbody = NewTagClass('Tbody')
Tfoot = NewTagClass('Tfoot')
Th = NewTagClass('Th')
Tr = NewTagClass('Tr')
Td = NewTagClass('Td')

# List tags
Ol = NewTagClass('Ol')
Ul = NewTagClass('Ul')
Li = NewTagClass('Li')

# Definition-list tags
Dl = NewTagClass('Dl')
Dt = NewTagClass('Dt')
Dd = NewTagClass('Dd')

# Form tags
Form = NewTagClass('Form')
Label = NewTagClass('Label')
Option = NewTagClass('Option')
Select = NewTagClass('Select')

# Building blocks
Container = Div
Wrapper = Div
Row = Div

