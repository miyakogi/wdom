#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from asyncio import coroutine, Future, ensure_future
from typing import Callable, Optional

from wdom.event import EventListener
from wdom.node import HTMLElement, Node

logger = logging.getLogger(__name__)
elements = dict()


class WebElement(HTMLElement):
    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id:str):
        self._id = id

    def __init__(self, *args, parent=None, **kwargs):
        self.id = kwargs.pop('id', str(id(self)))
        self.listeners = dict()
        super().__init__(*args, **kwargs)
        elements[self.id] = self
        if parent is not None:
            parent.appendChild(self)

    def _get_attrs_by_string(self) -> str:
        attrs_str = ' '.join((super()._get_attrs_by_string(),
                              'id="{}"'.format(self.id)))
        for event in self.listeners:
            attrs_str += ' on{event}="W.on{event}(this);"'.format(event=event)
        return attrs_str.strip()

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

    def empty(self):
        if self.connected:
            self.js_exec('empty')
        for child in tuple(self.childNodes):
            super().removeChild(child)

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

    def appendChild(self, child: 'WebElement'):
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.
        '''
        if self.connected:
            if isinstance(child, Node):
                self.js_exec('append', html=child.html)
            else:
                self.js_exec('append', html=str(child))
        super().appendChild(child)

    def insertBefore(self, child: 'WebElement', ref_node: 'WebElement'):
        '''Insert new child node before the reference child node. If the
        reference node is not a child of this node, raise ValueError. If this
        instance is connected to the node on browser, the child node is also
        added to it.
        '''
        if self.connected:
            if isinstance(child, Node):
                self.js_exec('insertBefore', html=child.html, id=ref_node.id)
            else:
                self.js_exec('insertBefore', html=str(child), id=ref_node.id)
        super().insertBefore(child, ref_node)

    def removeChild(self, child: 'Tag'):
        '''Remove the child node from this node. If the node is not a child
        of this node, raise ValueError.'''
        if isinstance(child, WebElement) and self.connected:
            self.js_exec('removeChild', id=child.id)
        super().removeChild(child)

    @property
    def textContent(self) -> str:
        '''Return text contents of this node and all chid nodes. Any value is
        set to this property, all child nodes are removed and new value is set
        as a text node.
        '''
        return HTMLElement.textContent.fget(self)

    @textContent.setter
    def textContent(self, text: str):
        HTMLElement.textContent.fset(self, text)
        if self.connected:
            self.js_exec(method='empty')
            self.js_exec(method='appendChild', html=self.textContent)

    @property
    def innerHTML(self) -> str:
        return HTMLElement.innerHTML.fget(self)

    @innerHTML.setter
    def innerHTML(self, html:str):
        HTMLElement.innerHTML.fset(self, html)
        if self.connected:
            self.js_exec(method='empty')
            self.js_exec(method='appendChild', html=html)
