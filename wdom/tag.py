#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from collections import Iterable
from functools import partial
from asyncio import coroutine, ensure_future, iscoroutine, Future
from inspect import iscoroutinefunction
from typing import Callable, Tuple, Optional, Union

from wdom.node import Node, Text, DOMTokenList
from wdom.web_node import WebElement

logger = logging.getLogger(__name__)


class TagBaseMeta(type):
    '''Meta class to set default class variable of HtmlDom'''
    def __prepare__(name, bases, **kwargs) -> dict:
        return {'inherit_class': True}


class Tag(WebElement, metaclass=TagBaseMeta):
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
                if issubclass(base_cls, Tag):
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
