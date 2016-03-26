#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncio import coroutine, Future
from typing import Optional
from xml.dom import Node

__all__ = ('Node', 'WebIF')


class WebIF:
    @property
    def connected(self) -> bool:
        raise NotImplementedError
    def on_message(self, msg:dict) -> None:
        raise NotImplementedError
    def js_exec(self, method:str, **kwargs) -> Optional[Future]:
        raise NotImplementedError
    def js_query(self, query:str) -> Future:
        raise NotImplementedError
    @coroutine
    def ws_send(self, obj) -> None:
        raise NotImplementedError
