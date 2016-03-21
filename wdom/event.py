#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncio import ensure_future, iscoroutinefunction
from typing import Callable


class Event:
    def __init__(self, type:str, **kwargs):
        self.type = type
        self.__dict__.update(kwargs)

    def stopPrapagation(self):
        raise NotImplementedError


class EventListener:
    '''Class to wrap an event listener. Acceptable listeners are function,
    coroutine, and coroutine-function. If ``apply_data`` is True, ``data`` is
    applied as a keyword argument of ``data`` when the registered event is
    triggered.'''
    # Should support generator?
    def __init__(self, listener: Callable):
        self.listener = listener

        if iscoroutinefunction(self.listener):
            self.action = self.wrap_coro_func(self.listener)
            self._is_coroutine = True
        else:
            self.action = self.listener
            self._is_coroutine = False

    def wrap_coro_func(self, coro) -> Callable:
        def wrapper(*args, **kwargs):
            nonlocal coro
            return ensure_future(coro(*args, **kwargs))
        return wrapper

    def __call__(self, event:Event):
        return self.action(event=event)


class EventTarget:
    def __init__(self, *args, **kwargs):
        self._listeners = {}
        super().__init__(*args, **kwargs)

    def _add_event_listener(self, event:str, listener:Callable):
        self._listeners.setdefault(event, []).append(EventListener(listener))

    def addEventListener(self, event:str, listener:Callable):
        self._add_event_listener(event, listener)

    def _remove_event_listener(self, event:str, listener:Callable):
        listeners = self._listeners.get(event)
        if not listeners:
            return
        for l in listeners:
            if l.listener == listener:
                listeners.remove(l)
                break
        if not listeners:
            del self._listeners[event]

    def removeEventListener(self, event:str, listener:Callable):
        self._remove_event_listener(event, listener)

    def _dispatch_event(self, event:Event):
        _tasks = []
        for listener in self._listeners.get(event.type, []):
            if listener._is_coroutine:
                _tasks.append(listener(event))
            else:
                listener(event)
        return _tasks

    def dispatchEvent(self, event:Event):
        return self._dispatch_event(event)
