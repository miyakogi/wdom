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
elements = {}


class TagBaseMeta(type):
    '''Meta class to set default class variable of HtmlDom'''
    def __prepare__(name, bases, **kwargs) -> dict:
        return {'inherit_class': True}


class TagBase(HTMLElement, metaclass=TagBaseMeta):
    '''Base class for html tags. ``HTMLElement`` requires to specify tag name
    when instanciate it, but this class and sublasses have default tag name and
    not need to specify it for each thier instances.

    Additionally, this class provides shortcut properties to handle some
    special attributes (class, type, is).
    '''
    #: Tag name used for this node.
    tag = 'tag'
    #: str and list of strs are acceptale.
    class_ = ''
    #: Inherit classes defined in super class or not.
    #: By default, this variable is True.
    inherit_class = True
    #: use for <input> tag's type
    type_ = ''
    #: custom element which extends built-in tag (like <table is="your-tag">)
    is_ = ''

    def __init__(self, *args, parent=None, **kwargs):
        attrs = kwargs.pop('attrs', None)
        if attrs:
            kwargs.update(attrs)
        if self.type_ and 'type' not in kwargs:
            kwargs['type'] = self.type_
        super().__init__(self.tag, parent=parent, **kwargs)
        for arg in args:
            self.appendChild(arg)

    @classmethod
    def get_class_list(cls) -> DOMTokenList:
        '''Return class-level class list, including all super class's.
        '''
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
        '''Shortcut method of ``appendChild``.'''
        self.appendChild(child)

    def insert(self, pos:int, child:Node):
        if isinstance(child, str):
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
    '''Add ``id`` attribute automatically.'''
    tag = 'py-node'

    def __init__(self, *args, **kwargs):
        self._id = kwargs.pop('id', str(id(self)))
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id:str):
        self._id = id

    def _get_attrs_by_string(self) -> str:
        return ' '.join((super()._get_attrs_by_string(),
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
    '''Base class for binding python node and dom object on browser. Any
    changes of this node are reflected on browser's one, and vice versa.
    '''
    tag = 'node'
    '''tag name of this node. For example, if ``tag = 'a'``, this node makes
    ``<a>`` tag on browser.
    '''

    def __init__(self, *args, parent=None, **kwargs):
        self.listeners = dict()
        super().__init__(*args, **kwargs)
        elements[self.id] = self
        if parent is not None:
            parent.appendChild(self)

    def _get_attrs_by_string(self) -> str:
        attrs_str = super()._get_attrs_by_string()
        for event in self.listeners:
            attrs_str += ' on{event}="W.on{event}(this);"'.format(event=event)
        return attrs_str

    @property
    def connected(self) -> bool:
        '''When this instance has any connection, return True.'''
        return self.ownerDocument is not None and any(self.ownerDocument.connections)

    @coroutine
    def on_message(self, msg: dict):
        '''Coroutine to be called when webscoket get message.'''
        logger.debug('WS MSG  {tag}: {msg}'.format(tag=self.tag, msg=msg))

        event = msg.get('event', False)
        if event:
            data = msg.get('data')
            for listener in self.listeners.get(event, []):
                listener(data=data)

    def addEventListener(self, event: str, listener: Callable):
        '''Add event listener to this node. ``event`` is a string which
        determines the event type when the new listener called. Acceptable
        events are same as JavaScript, without ``on``. For example, to add a
        listener which is called when this node is clicked, event is
        ``'click``.
        '''
        if event not in self.listeners:
            self.listeners[event] = []
            if self.connected:
                self.js_exec('addEventListener', event=event)
        self.listeners[event].append(EventListener(listener))

    def removeEventListener(self, event: str, listener: Callable):
        '''Remove an event listener of this node. The listener is removed only
        when both event type and listener is matched.
        '''
        listeners = self.listeners[event]
        for l in listeners:
            if l.listener == listener:
                listeners.remove(l)
                break
        if len(listeners) == 0:
            del self.listeners[event]

    def js_exec(self, method: str, **kwargs) -> Optional[Future]:
        '''Execute ``method`` in the related node on browser, via web socket
        connection. Other keyword arguments are passed to ``params`` attribute.
        If this node is not in any document tree (namely, this node does not
        have parent node), the ``method`` is not executed.
        '''
        if self.parent is not None:
            return ensure_future(
                self.ws_send(dict(method=method, params=kwargs))
            )

    @coroutine
    def ws_send(self, obj):
        '''Send message to the related nodes on browser, with ``tagname`` and
        ``id`` which specifies relation between python's object and element
        on browser. The message is serialized by JSON object and send via
        WebSocket connection.
        '''
        obj['id'] = self.id
        obj['tag'] = self.tag
        msg = json.dumps(obj)
        for conn in self.ownerDocument.connections:
            conn.write_message(msg)

    def insert(self, pos: int, new_child):
        '''Insert child node at the specified ``position``. The same operation
        will be done also in the related node on browser, if exists.
        '''
        if self.connected:
            self.js_exec('insert', index=pos, html=self[pos].html)
        super().insert(pos, new_child)

    def remove(self, *args, **kwargs):
        '''Remove this node from parent's DOM tree.
        '''
        if self.connected:
            fut = self.js_exec('remove')
            fut.add_done_callback(self._remove_callback)
        else:
            super().remove()

    def _remove_callback(self, *args, **kwargs):
        super().remove()

    def removeAttribute(self, attr: str):
        '''Remove attribute. Even if this node does not have the attribute,
        this method does not raise any error errors will be raised.
        '''
        if self.connected:
            self.js_exec('removeAttribute', attr=attr)
        super().removeAttribute(attr)

    def setAttribute(self, attr: str, value: str, **kwargs):
        '''Set attribute to ``value``. If the attribute already exists,
        overwrite it by new ``value``.
        '''
        if self.connected:
            self.js_exec('setAttribute', attr=attr, value=value)
        super().setAttribute(attr, value)

    def appendChild(self, child: 'Tag'):
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.
        '''
        super().appendChild(child)
        if self.connected:
            self.js_exec('append', html=self[-1].html)

    def insertBefore(self, child: 'Tag', ref_node: 'Tag'):
        '''Insert new child node before the reference child node. If the
        reference node is not a child of this node, raise ValueError. If this
        instance is connected to the node on browser, the child node is also
        added to it.
        '''
        super().insertBefore(child, ref_node)
        if self.connected:
            self.js_exec('insertBefore', html=child.html, id=ref_node.id)

    def removeChild(self, child: 'Tag'):
        '''Remove the child node from this node. If the node is not a child
        of this node, raise ValueError.'''
        if isinstance(child, Tag) and self.connected:
            self.js_exec('removeChild', id=child.id)
        super().removeChild(child)

    @property
    def textContent(self) -> str:
        '''Return text contents of this node and all chid nodes. Any value is
        set to this property, all child nodes are removed and new value is set
        as a text node.
        '''
        return PyNode.textContent.fget(self)

    @textContent.setter
    def textContent(self, text: str):
        PyNode.textContent.fset(self, text)
        if self.connected:
            self.js_exec(method='textContent', text=text)

    def show(self, **kwargs):
        '''Make this node visible on browser.'''
        self.attributes['hidden'] = False
        if self.connected:
            self.js_exec('show')

    def hide(self, **kwargs):
        '''Make this node invisible on browser.'''
        self.attributes['hidden'] = True
        if self.connected:
            self.js_exec('hide')

    def addClass(self, cls: str, **kwargs):
        '''Add a class to this node. If this node already has the class, or
        class name is empty string, do nothing.
        '''
        if cls and cls not in self.classList:
            if self.connected:
                self.js_exec('addClass', **{'class': cls})
            super().addClass(cls)

    def removeClass(self, cls: str, **kwargs):
        '''Remove the class from this node. If the class is not a member of
        this node's class or it is empty string, do nothing.
        '''
        if cls and  cls in self.classList:
            if self.connected:
                self.js_exec('removeClass', **{'class': cls})
            super().removeClass(cls)


def NewTagClass(class_name: str, tag: str=None, bases: Tuple[type]=(Tag, ),
                 **attrs) -> type:
    '''Generate and return new ``Tag`` class. If ``tag`` is empty, lower case
    of ``class_name`` is used for a tag name of the new class. ``bases`` should
    be a tuple of base classes. If it is empty, use ``Tag`` class for a base
    class. Other keyword arguments are used for class variables of the new
    class.

    Example::

        MyButton = NewTagClass(
                        'MyButton', 'button', (Button,), class_='btn')
        my_button = MyButton('Click!')
        print(my_button.html)

        >>> <button class="btn" id="111111111">Click!</button>
    '''
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
    '''Base class for ``<input>`` element.
    '''
    tag = 'input'
    #: type attribute; text, button, checkbox, or radio... and so on.
    type_ = ''

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
        '''If checked, this property returns True. Setting True/False to this
        property will change default value of this element.
        This node is other than checkbox or radio, this property will be
        ignored.
        '''
        return self.getAttribute('checked') or False

    @checked.setter
    def checked(self, value: bool):
        self.setAttribute('checked', value)

    @property
    def value(self) -> str:
        '''Get input value of this node. This value is used as a default value
        of this element.
        '''
        return self.getAttribute('value') or ''

    @value.setter
    def value(self, value: str):
        self.setAttribute('value', value)


class TextArea(Input):
    '''Base class for ``<textarea>`` element.'''
    tag = 'textarea'

    @property
    def value(self) -> str:
        '''Get input value of this node. This value is used as a default value
        of this element.
        '''
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

