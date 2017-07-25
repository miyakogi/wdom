#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from asyncio import ensure_future, iscoroutinefunction, Future
from typing import Any, Awaitable, Callable, List, Union, TYPE_CHECKING

from wdom.interface import Event
from wdom.webif import WebIF

if TYPE_CHECKING:
    from typing import MutableMapping  # noqa

_EventListenerType = Union[Callable[[Event], None],
                           Callable[[Event], Awaitable[None]]]


class EventListener:
    '''Class to wrap an event listener. Acceptable listeners are function,
    coroutine, and coroutine-function. If ``apply_data`` is True, ``data`` is
    applied as a keyword argument of ``data`` when the registered event is
    triggered.'''
    # Should support generator?
    def __init__(self, listener: _EventListenerType) -> None:
        self.listener = listener

        if iscoroutinefunction(self.listener):
            self.action = self.wrap_coro_func(self.listener)  # type: ignore
            self._is_coroutine = True
        else:
            self.action = self.listener  # type: ignore
            self._is_coroutine = False

    def wrap_coro_func(self, coro: Callable[[Event], Awaitable]
                       ) -> Callable[[Event], Awaitable]:
        def wrapper(e: Event) -> Future:
            return ensure_future(coro(e))
        return wrapper

    def __call__(self, event: Event) -> Awaitable[None]:
        return self.action(event)


class EventTarget:
    _listeners = None  # type: MutableMapping[str, List[EventListener]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._listeners = defaultdict(list)
        super().__init__(*args, **kwargs)  # type: ignore

    def _add_event_listener(self, event: str, listener: _EventListenerType
                            ) -> None:
        self._listeners[event].append(EventListener(listener))

    def _add_event_listener_web(self, event: str) -> None:
        if isinstance(self, WebIF):
            self.js_exec('addEventListener', event)  # type: ignore

    def addEventListener(self, event: str, listener: _EventListenerType
                         ) -> None:
        '''Add event listener to this node. ``event`` is a string which
        determines the event type when the new listener called. Acceptable
        events are same as JavaScript, without ``on``. For example, to add a
        listener which is called when this node is clicked, event is
        ``'click``.
        '''
        self._add_event_listener(event, listener)
        self._add_event_listener_web(event)

    def _remove_event_listener(self, event: str, listener: _EventListenerType
                               ) -> None:
        listeners = self._listeners[event]
        if not listeners:
            return
        for l in listeners:
            if l.listener == listener:
                listeners.remove(l)
                break
        if not listeners:
            del self._listeners[event]

    def _remove_event_listener_web(self, event: str) -> None:
        if isinstance(self, WebIF) and event not in self._listeners:
            self.js_exec('removeEventListener', event)  # type: ignore

    def removeEventListener(self, event: str, listener: _EventListenerType
                            ) -> None:
        '''Remove an event listener of this node. The listener is removed only
        when both event type and listener is matched.
        '''
        self._remove_event_listener(event, listener)
        self._remove_event_listener_web(event)

    def _dispatch_event(self, event: Event) -> List[Awaitable[None]]:
        _tasks = []
        for listener in self._listeners[event.type]:
            if listener._is_coroutine:
                _tasks.append(listener(event))
            else:
                listener(event)
        return _tasks

    def dispatchEvent(self, event: Event) -> List[Awaitable[None]]:
        return self._dispatch_event(event)
