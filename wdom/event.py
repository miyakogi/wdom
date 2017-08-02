#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""Event related classes."""

from collections import defaultdict
from asyncio import ensure_future, iscoroutinefunction, Future
from typing import Any, Awaitable, Callable, Dict, Optional, Union
from typing import TYPE_CHECKING

from wdom.node import Node

if TYPE_CHECKING:
    from typing import List, MutableMapping  # noqa: F401


# EventMsgDict = TypedDict('EventMsgDict', {
#     'proto': str,
#     'type': str,
#     'currentTarget': Dict[str, str],
#     'target': Dict[str, str],
# })
EventMsgDict = Dict[str, Any]


class Event:
    """Event interface class."""

    @property
    def currentTarget(self) -> Optional[Node]:
        """Return current event target."""
        return self.__currentTarget

    @property
    def target(self) -> Optional[Node]:
        """Return original event target, which emitted this event first."""
        return self.__target

    def __init__(self, type: str, init: EventMsgDict = None) -> None:
        """Create event object.

        First argument (type) is a string to represents type of this event.
        Second optional argument (init) is a dictionally, which has fields for
        this event's status.
        """
        from wdom.document import getElementByRimoId
        self.type = type
        self.init = dict() if init is None else init
        _id = self.init.get('currentTarget', {'id': None}).get('id')
        ctarget = getElementByRimoId(_id)
        self.__currentTarget = ctarget
        _id = self.init.get('target', {'id': None}).get('id')
        self.__target = getElementByRimoId(_id) or ctarget

    def stopPrapagation(self) -> None:
        """Not implemented yet."""
        raise NotImplementedError


class UIEvent(Event):  # noqa: D204
    """Super class of user input related events.

    Mouse/Touch/Focus/Keyboard/Wheel/Input/Composition/...Events are
    descendants of this class.
    """
    pass


class MouseEvent(UIEvent):  # noqa: D204
    """Mouse event class."""
    pass


class DragEvent(MouseEvent):  # noqa: D204
    """Drag event class."""
    pass


class KeyboardEvent(UIEvent):  # noqa: D204
    """Keyboard event class."""
    pass


class InputEvent(UIEvent):  # noqa: D204
    """Input event class."""
    pass


proto_dict = {
    'MouseEvent': MouseEvent,
    'DragEvent': DragEvent,
    'KeyboardEvent': KeyboardEvent,
    'InputEvent': InputEvent,
}


def create_event(msg: EventMsgDict) -> Event:
    """Create Event from JSOM msg and set target nodes.

    :arg EventTarget currentTarget: Current event target node.
    :arg EventTarget target: Node which emitted this event first.
    :arg dict init: Event options.
    """
    proto = msg.get('proto', '')  # type: str
    cls = proto_dict.get(proto, Event)
    e = cls(msg['type'], msg)
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

    Acceptable listeners are function, coroutine, and coroutine-function.
    If listener is a coroutine or coroutine-function, it will be executed
    synchronously as if it is normal function.
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

    _event_listeners = None  # type: MutableMapping[str, List[EventListener]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        # need to call super().__init__ to use as mixin class
        super().__init__(*args, **kwargs)  # type: ignore
        self._event_listeners = defaultdict(list)

    def _add_event_listener(self, event: str, listener: _EventListenerType
                            ) -> None:
        self._event_listeners[event].append(EventListener(listener))

    def addEventListener(self, event: str, listener: _EventListenerType
                         ) -> None:
        """Add event listener to this node.

        ``event`` is a string which determines the event type when the new
        listener called. Acceptable events are same as JavaScript, without
        ``on``. For example, to add a listener which is called when this node
        is clicked, event is ``'click``.
        """
        self._add_event_listener(event, listener)

    def _remove_event_listener(self, event: str, listener: _EventListenerType
                               ) -> None:
        listeners = self._event_listeners[event]
        if not listeners:
            return
        for l in listeners:
            if l.listener == listener:
                listeners.remove(l)
                break
        if not listeners:
            del self._event_listeners[event]

    def removeEventListener(self, event: str, listener: _EventListenerType
                            ) -> None:
        """Remove an event listener of this node.

        The listener is removed only when both event type and listener is
        matched.
        """
        self._remove_event_listener(event, listener)

    def on_event_pre(self, event: Event) -> None:
        """Run before dispatching events.

        Used for seting values changed by user input, in some elements like
        input, textarea, or select. In this method, event.currentTarget is a
        dict sent from browser.
        """
        pass

    def _dispatch_event(self, event: Event) -> None:
        for listener in self._event_listeners[event.type]:
            listener(event)

    def dispatchEvent(self, event: Event) -> None:
        """Emit events."""
        self._dispatch_event(event)
