#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Base classes for web-synchronized Nodes."""

import logging
import re
from asyncio import Future
from typing import Any, Awaitable, Dict, Iterable, Optional, Union
from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

from wdom import server
from wdom.event import Event, create_event
from wdom.element import _AttrValueType, HTMLElement, ElementParser
from wdom.node import Node

if TYPE_CHECKING:
    from typing import Type  # noqa

logger = logging.getLogger(__name__)
_remove_id_re = re.compile(r' rimo_id="\d+"')
_RimoIdType = Union[int, str]
_T_MsgItem = Union[int, str]


def remove_rimo_id(html: str) -> str:
    """Remove ``rimo_id`` attribute from html strings."""
    return _remove_id_re.sub('', html)


class WebIF:
    """Web Interfase abstract class."""

    tag = None  # type: str

    @property
    def rimo_id(self) -> _T_MsgItem:  # noqa: D102
        ...  # for type check

    @property
    def ownerDocument(self) -> Optional[Node]:  # noqa: D102
        # for type check
        return None

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        self.__reqid = 0
        self.__tasks = {}  # type: Dict
        super().__init__(*args, **kwargs)  # type: ignore

    @property
    def connected(self) -> bool:
        """When this instance has any connection, return True."""
        return server.is_connected()

    def on_event_pre(self, event: Event) -> None:
        """Run before dispatching events.

        Used for seting values changed by user input, in some elements like
        input, textarea, or select. In this method, event.currentTarget is a
        dict sent from browser.
        """
        pass

    def on_response(self, msg: Dict[str, str]) -> None:
        """Run when get response from browser."""
        response = msg.get('data', False)
        if response:
            task = self.__tasks.pop(msg.get('reqid'), False)
            if task and not task.cancelled() and not task.done():
                task.set_result(msg.get('data'))

    def js_exec(self, method: str, *args: Union[int, str]) -> None:
        """Execute ``method`` in the related node on browser.

        Other keyword arguments are passed to ``params`` attribute.
        If this node is not in any document tree (namely, this node does not
        have parent node), the ``method`` is not executed.
        """
        if self.connected:
            self.ws_send(dict(method=method, params=args))

    def js_query(self, query: str) -> Awaitable:
        """Send query to related DOM on browser.

        :param str query: single string which indicates query type.
        """
        if self.connected:
            self.js_exec(query, self.__reqid)
            fut = Future()  # type: Future[str]
            self.__tasks[self.__reqid] = fut
            self.__reqid += 1
            return fut
        f = Future()  # type: Future[None]
        f.set_result(None)
        return f

    def ws_send(self, obj: Dict[str, Union[Iterable[_T_MsgItem], _T_MsgItem]]
                ) -> None:
        """Send ``obj`` as message to the related nodes on browser.

        :arg dict obj: Message is serialized by JSON object and send via
            WebSocket connection.
        """
        if self.ownerDocument is not None:
            obj['target'] = 'node'
            obj['id'] = self.rimo_id
            obj['tag'] = self.tag
            server.push_message(obj)


class WdomElementParser(ElementParser):
    """Parser class which generates WdomElement nodes."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        super().__init__(*args, **kwargs)
        self.default_class = WdomElement


class WdomElement(HTMLElement, WebIF):
    """WdomElement class.

    This class provides main features to synchronously control browser DOM
    node.
    """

    _elements_with_rimo_id = WeakValueDictionary(
    )  # type: WeakValueDictionary[_RimoIdType, WdomElement]
    _parser_class = WdomElementParser  # type: Type[ElementParser]

    @property
    def rimo_id(self) -> _RimoIdType:
        """Get rimo_id attribute.

        This attribute is used to relate python node and browser DOM node.
        """
        _id = self.getAttribute('rimo_id') or ''
        if not isinstance(_id, (int, str)):
            raise TypeError('Invalid rimo_id type')
        return _id

    @rimo_id.setter
    def rimo_id(self, id: _RimoIdType) -> None:
        self.setAttribute('rimo_id', id)

    def __init__(self, *args: Any, parent: Optional['WdomElement'] = None,
                 rimo_id: Optional[_RimoIdType] = None,
                 **kwargs: Any) -> None:  # noqa: D102
        super().__init__(*args, **kwargs)
        self.rimo_id = rimo_id or str(id(self))
        self.addEventListener('mount', self._on_mount)
        if parent:
            parent.appendChild(self)

    def __copy__(self) -> HTMLElement:
        clone = super().__copy__()
        if clone.rimo_id == str(id(self)):
            # change automatically added id
            # overhead in __init__...
            clone.rimo_id = str(id(clone))
        return clone

    def _on_mount(self, e: Event) -> None:
        for event in self._event_listeners:
            self._add_event_listener_web(event=event)

    def _set_attribute(self, attr: str, value: _AttrValueType) -> None:
        if attr == 'rimo_id':
            if 'rimo_id' in self.attributes:
                # remove old reference to self
                self._elements_with_rimo_id.pop(self.rimo_id, None)
            # register this elements with new id
            if isinstance(value, (int, str)):
                self._elements_with_rimo_id[value] = self
            else:
                raise TypeError('Invalid rimo_id type')
        super()._set_attribute(attr, value)

    def _remove_web(self) -> None:
        self.js_exec('remove')

    def remove(self) -> None:
        """Remove this node from parent's DOM tree."""
        self._remove_web()
        self._remove()

    def _empty_web(self) -> None:
        self.js_exec('empty')

    def empty(self) -> None:
        """Remove all child nodes from this node."""
        self._empty_web()
        self._empty()

    def _append_child_web(self, child: 'WdomElement') -> None:
        html = child.html if isinstance(child, Node) else str(child)
        self.js_exec('insertAdjacentHTML', 'beforeend', html)

    def appendChild(self, child: 'WdomElement') -> Node:
        """Append child node at the last of child nodes.

        If this instance is connected to the node on browser, the child node is
        also added to it.
        """
        self._append_child_web(child)
        return self._append_child(child)

    def _insert_before_web(self, child: Node, ref_node: Node) -> None:
        html = child.html if isinstance(child, Node) else str(child)
        if isinstance(ref_node, WdomElement):
            ref_node.js_exec('insertAdjacentHTML', 'beforebegin', html)
        else:
            index = self.index(ref_node)
            self.js_exec('insert', index, html)

    def insertBefore(self, child: Node, ref_node: Node) -> Node:
        """Insert new child node before the reference child node.

        If the reference node is not a child of this node, raise ValueError. If
        this instance is connected to the node on browser, the child node is
        also added to it.
        """
        self._insert_before_web(child, ref_node)
        return self._insert_before(child, ref_node)

    def _remove_child_web(self, child: Node) -> None:
        if child in self.childNodes:
            if isinstance(child, WdomElement):
                self.js_exec('removeChildById', child.rimo_id)
            else:
                self.js_exec('removeChildByIndex', self.index(child))

    def removeChild(self, child: Node) -> Node:
        """Remove the child node from this node.

        If the node is not a child of this node, raise ValueError.
        """
        self._remove_child_web(child)
        return self._remove_child(child)

    def _replace_child_web(self, new_child: Node, old_child: Node) -> None:
        if isinstance(old_child, WdomElement):
            self.js_exec('replaceChildById', new_child.html, old_child.rimo_id)
        elif old_child.parentNode is not None:
            # old_child will be Text Node
            index = old_child.parentNode.index(old_child)
            # Remove old_child before insert new child
            self._remove_child_web(old_child)
            self.js_exec('insert', index, new_child.html)

    def replaceChild(self, new_child: 'WdomElement', old_child: 'WdomElement'
                     ) -> Node:
        """Replace child nodes."""
        self._replace_child_web(new_child, old_child)
        return self._replace_child(new_child, old_child)

    async def getBoundingClientRect(self) -> None:
        """Get size of this node on browser."""
        fut = await self.js_query('getBoundingClientRect')
        return fut

    def _set_text_content_web(self, text: str) -> None:
        self.js_exec('textContent', self.textContent)

    @HTMLElement.textContent.setter  # type: ignore
    def textContent(self, text: str) -> None:  # type: ignore
        """Set textContent both on this node and related browser node."""
        self._set_text_content(text)
        self._set_text_content_web(text)

    def _set_inner_html_web(self, html: str) -> None:
        self.js_exec('innerHTML', html)

    @HTMLElement.innerHTML.setter  # type: ignore
    def innerHTML(self, html: str) -> None:  # type: ignore
        """Set innerHTML both on this node and related browser node."""
        df = self._parse_html(html)
        self._set_inner_html_web(df.html)
        self._empty()
        self._append_child(df)

    @property
    def html_noid(self) -> str:
        """Get html representation of this node without rimo_id."""
        return remove_rimo_id(self.html)

    def click(self) -> None:
        """Send click event."""
        if self.connected:
            self.js_exec('click')
        else:
            # Web上に表示されてれば勝手にブラウザ側からクリックイベント発生する
            # のでローカルのクリックイベント不要
            e = create_event('click', currentTarget=self, target=self)
            self._dispatch_event(e)

    def exec(self, script: str) -> None:
        """Execute JavaScript on the related browser node."""
        self.js_exec('eval', script)

    # Window controll
    def scroll(self, x: int, y: int) -> None:  # noqa: D102
        self.js_exec('scroll', x, y)

    def scrollTo(self, x: int, y: int) -> None:  # noqa: D102
        self.js_exec('scrollTo', x, y)

    def scrollBy(self, x: int, y: int) -> None:  # noqa: D102
        self.js_exec('scrollBy', x, y)

    def scrollX(self) -> Awaitable:  # noqa: D102
        return self.js_query('scrollX')

    def scrollY(self) -> Awaitable:  # noqa: D102
        return self.js_query('scrollY')
