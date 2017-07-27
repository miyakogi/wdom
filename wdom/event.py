#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""Event related classes."""

from collections import defaultdict
from asyncio import ensure_future, iscoroutinefunction, Future
from typing import Any, Awaitable, Callable, List, Optional, Union  # noqa
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import MutableMapping  # noqa
    from wdom.node import Node  # noqa


class Event:
    """Event interface class."""

    currentTarget = None  # type: Optional[Node]
    target = None  # type: Optional[Node]

    def __init__(self, type: str, init: Optional[dict] = None) -> None:
        """Create event object.

        First argument (type) is a string to represents type of this event.
        Second optional argument (init) is a dictionally, which has fields for
        this event's status.
        """
        self.type = type
        self.init = dict() if init is None else init  # type: dict

    def stopPrapagation(self) -> None:
        """Not implemented yet."""
        raise NotImplementedError


def create_event(type: str, *,
                 currentTarget: Optional['Node'] = None,
                 target: Optional['Node'] = None,
                 init: Optional[dict] = None
                 ) -> Event:
    """Create Event and set target nodes."""
    e = Event(type, init)
    e.currentTarget = currentTarget
    e.target = target
    return e


_EventListenerType = Union[Callable[[Event], None],
                           Callable[[Event], Awaitable[None]]]


def _wrap_coro_func(coro: Callable[[Event], Awaitable]
                    ) -> Callable[[Event], Awaitable]:
    def wrapper(e: Event) -> Future:
        return ensure_future(coro(e))
    return wrapper


class EventListener:
    """Class to wrap an event listener function.

    Acceptable listeners are function, coroutine, and coroutine-function. If
    ``apply_data`` is True, ``data`` is applied as a keyword argument of
    ``data`` when the registered event is triggered.
    """

    # Should support generator?
    def __init__(self, listener: _EventListenerType) -> None:
        """Wrap an event listener.

        Event listener should be function or coroutine-function.
        """
        self.listener = listener
        if iscoroutinefunction(self.listener):
            self.action = _wrap_coro_func(self.listener)  # type: ignore
            self._is_coroutine = True
        else:
            self.action = self.listener  # type: ignore
            self._is_coroutine = False

    def __call__(self, event: Event) -> Awaitable[None]:
        """Execute wrapped event listener.

        Pass event object to the listener as a first argument.
        """
        return self.action(event)


class EventTarget:
    """Base class for EventTargets.

    This class and subclasses can add/remove event listeners and emit events.
    """

    _listeners = None  # type: MutableMapping[str, List[EventListener]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        self._listeners = defaultdict(list)
        super().__init__(*args, **kwargs)  # type: ignore

    def _add_event_listener(self, event: str, listener: _EventListenerType
                            ) -> None:
        self._listeners[event].append(EventListener(listener))

    def _add_event_listener_web(self, event: str) -> None:
        from wdom.web_node import WebIF
        if isinstance(self, WebIF):
            self.js_exec('addEventListener', event)  # type: ignore

    def addEventListener(self, event: str, listener: _EventListenerType
                         ) -> None:
        """Add event listener to this node.

        ``event`` is a string which determines the event type when the new
        listener called. Acceptable events are same as JavaScript, without
        ``on``. For example, to add a listener which is called when this node
        is clicked, event is ``'click``.
        """
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
        from wdom.web_node import WebIF
        if isinstance(self, WebIF) and event not in self._listeners:
            self.js_exec('removeEventListener', event)  # type: ignore

    def removeEventListener(self, event: str, listener: _EventListenerType
                            ) -> None:
        """Remove an event listener of this node.

        The listener is removed only when both event type and listener is
        matched.
        """
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
        """Emit events."""
        return self._dispatch_event(event)
