#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from asyncio import Future
from typing import Any, Dict, Iterable, Optional, Union, Awaitable
from xml.dom import Node

from wdom import server
from wdom.interface import Event

logger = logging.getLogger(__name__)
_T_MsgItem = Union[int, str]


class WebIF:
    tag = None  # type: str

    @property
    def rimo_id(self) -> _T_MsgItem: ...  # for type check

    @property
    def ownerDocument(self) -> Optional[Node]:
        return None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._reqid = 0
        self._tasks = {}  # type: Dict
        super().__init__(*args, **kwargs)  # type: ignore

    @property
    def connected(self) -> bool:
        '''When this instance has any connection, return True.'''
        return server.is_connected()

    def on_event_pre(self, event: Event) -> None:
        '''Hook executed before dispatching events.
        Used for set values changed by user input, in some elements like input,
        textarea, or select.
        In this method, event.currentTarget is a dict sent from browser.
        '''
        pass

    def on_response(self, msg: Dict[str, str]) -> None:
        response = msg.get('data', False)
        if response:
            task = self._tasks.pop(msg.get('reqid'), False)
            if task and not task.cancelled() and not task.done():
                task.set_result(msg.get('data'))

    def js_exec(self, method: str, *args: Union[int, str]) -> None:
        '''Execute ``method`` in the related node on browser, via web socket
        connection. Other keyword arguments are passed to ``params`` attribute.
        If this node is not in any document tree (namely, this node does not
        have parent node), the ``method`` is not executed.
        '''
        if self.connected:
            self.ws_send(dict(method=method, params=args))

    def js_query(self, query: str) -> Awaitable:
        if self.connected:
            self.js_exec(query, self._reqid)
            fut = Future()  # type: Future[str]
            self._tasks[self._reqid] = fut
            self._reqid += 1
            return fut
        else:
            f = Future()  # type: Future[None]
            f.set_result(None)
            return f

    def ws_send(self, obj: Dict[str, Union[Iterable[_T_MsgItem], _T_MsgItem]]
                ) -> None:
        '''Send message to the related nodes on browser, with ``tagname`` and
        ``id`` which specifies relation between python's object and element
        on browser. The message is serialized by JSON object and send via
        WebSocket connection.
        '''
        if self.ownerDocument is not None:
            obj['target'] = 'node'
            obj['id'] = self.rimo_id
            obj['tag'] = self.tag
            server.push_message(obj)
