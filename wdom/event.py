#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncio import ensure_future, iscoroutine, iscoroutinefunction
from typing import Callable


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



