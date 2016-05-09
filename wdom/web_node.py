#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
from typing import Union
from asyncio import coroutine
from weakref import WeakValueDictionary

from wdom.interface import Event
from wdom.node import Node
from wdom.webif import WebIF
from wdom.element import HTMLElement

logger = logging.getLogger(__name__)
remove_id_re = re.compile(r' rimo_id="\d+"')


class WebElement(HTMLElement, WebIF):
    _elements_with_rimo_id = WeakValueDictionary()

    @property
    def rimo_id(self) -> str:
        return self.getAttribute('rimo_id') or ''

    @rimo_id.setter
    def rimo_id(self, id: Union[str, int]):
        self.setAttribute('rimo_id', id)

    def __init__(self, *args, parent=None, rimo_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rimo_id = rimo_id or str(id(self))
        self.addEventListener('mount', self._on_mount)
        if parent:
            parent.appendChild(self)

    def __copy__(self) -> HTMLElement:
        clone = super().__copy__()
        if clone.rimo_id == str(id(self)):
            # change automatically added id
            # overhead in __init__...
            clone.rimo_id = str(id(clone))
        return clone

    def _on_mount(self, *args, **kwargs):
        for event in self._listeners:
            self._add_event_listener_web(event=event)

    def _set_attribute(self, attr: str, value: str):
        if attr == 'rimo_id':
            if 'rimo_id' in self.attributes:
                # remove old reference to self
                self._elements_with_rimo_id.pop(self.rimo_id, None)
            # register this elements with new id
            self._elements_with_rimo_id[value] = self
        super()._set_attribute(attr, value)

    def _remove_web(self):
        self.js_exec('remove')

    def remove(self, *args, **kwargs):
        '''Remove this node from parent's DOM tree.
        '''
        self._remove_web()
        self._remove()

    def _empty_web(self):
        self.js_exec('empty')

    def empty(self):
        self._empty_web()
        self._empty()

    def _append_child_web(self, child: 'WebElement'):
        html = child.html if isinstance(child, Node) else str(child)
        self.js_exec('insertAdjacentHTML', 'beforeend', html)

    def appendChild(self, child: 'WebElement') -> Node:
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.
        '''
        self._append_child_web(child)
        return self._append_child(child)

    def _insert_before_web(self, child: Node, ref_node: Node):
        html = child.html if isinstance(child, Node) else str(child)
        if isinstance(ref_node, WebElement):
            ref_node.js_exec('insertAdjacentHTML', 'beforebegin', html)
        else:
            index = self.index(ref_node)
            self.js_exec('insert', index, html)

    def insertBefore(self, child: Node, ref_node: Node) -> Node:
        '''Insert new child node before the reference child node. If the
        reference node is not a child of this node, raise ValueError. If this
        instance is connected to the node on browser, the child node is also
        added to it.
        '''
        self._insert_before_web(child, ref_node)
        return self._insert_before(child, ref_node)

    def _remove_child_web(self, child: Node):
        if child in self.childNodes:
            if isinstance(child, WebElement):
                self.js_exec('removeChildById', child.rimo_id)
            else:
                self.js_exec('removeChildByIndex', self.index(child))

    def removeChild(self, child: Node) -> Node:
        '''Remove the child node from this node. If the node is not a child
        of this node, raise ValueError.'''
        self._remove_child_web(child)
        return self._remove_child(child)

    def _replace_child_web(self, new_child: Node, old_child: Node):
        if isinstance(old_child, WebElement):
            self.js_exec('replaceChildById', new_child.html, old_child.rimo_id)
        else:
            # old_child will be Text Node
            index = old_child.parentNode.index(old_child)
            # Remove old_child before insert new child
            self._remove_child_web(old_child)
            self.js_exec('insert', index, new_child.html)

    def replaceChild(self, new_child, old_child) -> Node:
        self._replace_child_web(new_child, old_child)
        return self._replace_child(new_child, old_child)

    @coroutine
    def getBoundingClientRect(self):
        fut = yield from self.js_query('getBoundingClientRect')
        return fut

    @property
    def textContent(self) -> str:
        '''Return text contents of this node and all chid nodes. Any value is
        set to this property, all child nodes are removed and new value is set
        as a text node.
        '''
        return self._get_text_content()

    def _set_text_content_web(self, text: str):
        self.js_exec('textContent', self.textContent)

    @textContent.setter
    def textContent(self, text: str):
        self._set_text_content(text)
        self._set_text_content_web(text)

    def _set_inner_html_web(self, html: str):
        self.js_exec('innerHTML', html)

    @property
    def innerHTML(self) -> str:
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html: str):
        self._set_inner_html_web(html)
        self._set_inner_html(html)

    @property
    def html_noid(self) -> str:
        return remove_id_re.sub('', self.html)

    def click(self):
        if self.connected:
            self.js_exec('click')
        else:
            self._dispatch_event(Event('click'))

    def exec(self, script):
        self.js_exec('eval', script)

    # Window controll
    def scroll(self, x: int, y: int):
        self.js_exec('scroll', x, y)

    def scrollTo(self, x: int, y: int):
        self.js_exec('scrollTo', x, y)

    def scrollBy(self, x: int, y: int):
        self.js_exec('scrollBy', x, y)

    def scrollX(self):
        return self.js_query('scrollX')

    def scrollY(self):
        return self.js_query('scrollY')
