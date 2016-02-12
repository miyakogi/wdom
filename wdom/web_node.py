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
        self._reqid = 0
        self._tasks = {}
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

    def on_message(self, msg: dict):
        '''Coroutine to be called when webscoket get message.'''
        logger.debug('WS MSG  {tag}: {msg}'.format(tag=self.tag, msg=msg))

        msg_type = msg.get('type')
        if msg_type == 'event':
            ensure_future(self.handle_event(msg))
        elif msg_type == 'response':
            self.handle_response(msg)

    @coroutine
    def handle_event(self, msg):
        event = msg.get('event', False)
        if event:
            data = msg.get('data')
            for listener in self.listeners.get(event, []):
                listener(data=data)

    def handle_response(self, msg):
        response = msg.get('data', False)
        if response:
            req = self._tasks.pop(msg.get('reqid'), False)
            if req and not req.cancelled() and not req.done():
                req.set_result(msg.get('data'))

    def addEventListener(self, event: str, listener: Callable):
        '''Add event listener to this node. ``event`` is a string which
        determines the event type when the new listener called. Acceptable
        events are same as JavaScript, without ``on``. For example, to add a
        listener which is called when this node is clicked, event is
        ``'click``.
        '''
        if event not in self.listeners:
            self.listeners[event] = []
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
        if self.connected:
            return ensure_future(
                self.ws_send(dict(method=method, params=kwargs))
            )

    def _query(self, query):
        if self.connected:
            self.js_exec(query, reqid=self._reqid)
            fut = Future()
            self._tasks[self._reqid] = fut
            self._reqid += 1
            return fut
        else:
            fut = Future()
            fut.set_result(None)
            return fut

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
        if self.ownerDocument is not None:
            for conn in self.ownerDocument.connections:
                conn.write_message(msg)

    def insert(self, pos: int, new_child):
        '''Insert child node at the specified ``position``. The same operation
        will be done also in the related node on browser, if exists.
        '''
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

    def _empty_web(self):
        self.js_exec('empty')

    def empty(self):
        self._empty_web()
        self._empty()

    def removeAttribute(self, attr: str):
        '''Remove attribute. Even if this node does not have the attribute,
        this method does not raise any error errors will be raised.
        '''
        self.js_exec('removeAttribute', attr=attr)
        super().removeAttribute(attr)

    def setAttribute(self, attr: str, value: str, **kwargs):
        '''Set attribute to ``value``. If the attribute already exists,
        overwrite it by new ``value``.
        '''
        self.js_exec('setAttribute', attr=attr, value=value)
        super().setAttribute(attr, value)

    def _append_child_web(self, child: 'WebElement'):
        if isinstance(child, Node):
            text = child.html
        else:
            text = str(child)
        self.js_exec('insertAdjacentHTML', position='beforeend', text=text)

    def appendChild(self, child: 'WebElement'):
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.
        '''
        self._append_child_web(child)
        self._append_child(child)

    def _insert_before_web(self, child: 'WebElement', ref_node: 'WebElement'):
        if isinstance(child, WebElement):
            text = child.html
        else:
            text = str(child)
        if isinstance(ref_node, WebElement):
            ref_node.js_exec('insertAdjacentHTML', position='beforebegin',
                                text=text)
        else:
            index = self.childNodes.index(ref_node)
            self.insert(index, text)

    def insertBefore(self, child: 'WebElement', ref_node: 'WebElement'):
        '''Insert new child node before the reference child node. If the
        reference node is not a child of this node, raise ValueError. If this
        instance is connected to the node on browser, the child node is also
        added to it.
        '''
        self._insert_before_web(child, ref_node)
        self._insert_before(child, ref_node)

    def _remove_child_web(self, child: 'WebElement'):
        if isinstance(child, WebElement) and self.connected:
            self.js_exec('removeChild', id=child.id)

    def removeChild(self, child: 'Tag'):
        '''Remove the child node from this node. If the node is not a child
        of this node, raise ValueError.'''
        self._remove_child_web(child)
        self._remove_child(child)

    def _replace_child_web(self, new_child, old_child):
        # Does not work... why?
        # self._insert_before_web(new_child, old_child)
        # self._remove_child_web(old_child)
        # This also not work...
        # old_child.js_exec('outerHTML', html=new_child.html)
        self.js_exec('replaceChild', id=old_child.id, html=new_child.html)

    def replaceChild(self, new_child, old_child):
        self._replace_child_web(new_child, old_child)
        self._replace_child(new_child, old_child)

    @coroutine
    def getBoundingClientRect(self):
        fut = yield from self._query('getBoundingClientRect')
        return fut

    @property
    def textContent(self) -> str:
        '''Return text contents of this node and all chid nodes. Any value is
        set to this property, all child nodes are removed and new value is set
        as a text node.
        '''
        return self._get_text_content()

    def _set_text_content_web(self, text:str):
        self.js_exec(method='textContent', text=self.textContent)

    @textContent.setter
    def textContent(self, text: str):
        self._set_text_content(text)
        self._set_text_content_web(text)

    def _set_inner_html_web(self, html:str):
        self.js_exec(method='innerHTML', html=html)

    @property
    def innerHTML(self) -> str:
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html:str):
        self._set_inner_html_web(html)
        self._set_inner_html(html)

    @property
    def html_noid(self) -> str:
        html = self.start_tag.replace(' id="{}"'.format(self.id), '')
        html += ''.join(elm.html_noid if isinstance(elm, WebElement) else elm.html
                       for elm in self.childNodes)
        html += self.end_tag
        return html

    # Window controll
    def scroll(self, x:int, y:int):
        self.js_exec('scroll', x=x, y=y)

    def scrollTo(self, x:int, y:int):
        self.js_exec('scrollTo', x=x, y=y)

    def scrollBy(self, x:int, y:int):
        self.js_exec('scrollBy', x=x, y=y)

    def scrollX(self):
        return self._query('scrollX')

    @coroutine
    def scrollY(self):
        fut = yield from self._query('scrollY')
        return fut
