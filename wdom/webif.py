#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from asyncio import Future
from typing import Optional
from xml.dom import Node

from wdom import server
from wdom.interface import Event

logger = logging.getLogger(__name__)


class WebIF:
    @property
    def ownerDocument(self) -> Optional[Node]:
        return None

    def __init__(self, *args, **kwargs):
        self._reqid = 0
        self._tasks = {}
        super().__init__(*args, **kwargs)

    @property
    def connected(self) -> bool:
        '''When this instance has any connection, return True.'''
        return server.is_connected()

    def on_event_pre(self, event: Event):
        '''Hook executed before dispatching events.
        Used for set values changed by user input, in some elements like input,
        textarea, or select.
        In this method, event.currentTarget is a dict sent from browser.
        '''
        pass

    def on_response(self, msg):
        response = msg.get('data', False)
        if response:
            task = self._tasks.pop(msg.get('reqid'), False)
            if task and not task.cancelled() and not task.done():
                task.set_result(msg.get('data'))

    def js_exec(self, method: str, *args):
        '''Execute ``method`` in the related node on browser, via web socket
        connection. Other keyword arguments are passed to ``params`` attribute.
        If this node is not in any document tree (namely, this node does not
        have parent node), the ``method`` is not executed.
        '''
        if self.connected:
            self.ws_send(dict(method=method, params=args))

    def js_query(self, query) -> Future:
        if self.connected:
            self.js_exec(query, self._reqid)
            fut = Future()
            self._tasks[self._reqid] = fut
            self._reqid += 1
            return fut
        else:
            fut = Future()
            fut.set_result(None)
            return fut

    def ws_send(self, obj):
        '''Send message to the related nodes on browser, with ``tagname`` and
        ``id`` which specifies relation between python's object and element
        on browser. The message is serialized by JSON object and send via
        WebSocket connection.
        '''
        obj['target'] = 'node'
        obj['id'] = self.rimo_id
        obj['tag'] = self.tag
        msg = json.dumps(obj)
        server.send_message(msg)
