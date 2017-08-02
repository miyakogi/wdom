#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Base classes for web-synchronized Nodes."""

import logging
import re
from asyncio import Future
from typing import Any, Awaitable, Dict, Iterable, Optional, Tuple, Union
from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

from wdom import server
from wdom.event import Event, create_event, _EventListenerType, EventTarget
from wdom.element import _AttrValueType, HTMLElement, ElementParser
from wdom.element import ElementMeta, DOMTokenList
from wdom.node import Node, CharacterData

if TYPE_CHECKING:
    from typing import Type  # noqa

logger = logging.getLogger(__name__)
_remove_id_re = re.compile(r' rimo_id="\d+"')
_RimoIdType = Union[int, str]
_T_MsgItem = Union[int, str]


def remove_rimo_id(html: str) -> str:
    """Remove ``rimo_id`` attribute from html strings."""
    return _remove_id_re.sub('', html)


class WebIF(EventTarget):
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

    # Event Handling
    def _add_event_listener_web(self, event: str) -> None:
        self.js_exec('addEventListener', event)

    def addEventListener(self, event: str, listener: _EventListenerType
                         ) -> None:
        super().addEventListener(event, listener)
        self._add_event_listener_web(event)

    def _remove_event_listener_web(self, event: str) -> None:
        if event not in self._event_listeners:
            self.js_exec('removeEventListener', event)  # type: ignore

    def removeEventListener(self, event: str, listener: _EventListenerType
                            ) -> None:
        super().removeEventListener(event, listener)
        self._remove_event_listener_web(event)


class WdomElementParser(ElementParser):
    """Parser class which generates WdomElement nodes."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        super().__init__(*args, **kwargs)
        self.default_class = WdomElement


class WdomElementMeta(ElementMeta):
    """Meta class to set default class variable of HTMLElement."""

    @classmethod
    def __prepare__(metacls, name: str, bases: Tuple[type], **kwargs: Any
                    ) -> Dict[str, bool]:
        return {'inherit_class': True}


class WdomElement(HTMLElement, WebIF, metaclass=WdomElementMeta):
    """WdomElement class.

    This class provides main features to synchronously control browser DOM
    node.

    Additionally, this class provides shortcut properties to handle class
    attributes.
    """

    _elements_with_rimo_id = WeakValueDictionary(
    )  # type: WeakValueDictionary[_RimoIdType, WdomElement]
    _parser_class = WdomElementParser  # type: Type[ElementParser]

    #: str and list of strs are acceptale.
    class_ = ''
    #: Inherit classes defined in super class or not.
    #: By default, this variable is True.
    inherit_class = True

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
        for c in self.classList:
            clone.addClass(c)
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

    def __getitem__(self, attr: Union[str, int]
                    ) -> Union[Node, _AttrValueType]:
        """Get/Set/Remove access by subscription (node['attr'])."""
        if isinstance(attr, int):
            return self.childNodes[attr]
        return self.getAttribute(attr)

    def __setitem__(self, attr: str, val: _AttrValueType) -> None:
        self.setAttribute(attr, val)

    def __delitem__(self, attr: str) -> None:
        self.removeAttribute(attr)

    @classmethod
    def get_class_list(cls) -> DOMTokenList:
        """Get class-level class list, including all super class's."""
        cl = []
        cl.append(DOMTokenList(cls, cls.class_))
        if cls.inherit_class:
            for base_cls in cls.__bases__:
                if issubclass(base_cls, WdomElement):
                    cl.append(base_cls.get_class_list())
        # Reverse order so that parent's class comes to front  <- why?
        cl.reverse()
        return DOMTokenList(cls, *cl)

    def getAttribute(self, attr: str) -> _AttrValueType:  # noqa: D102
        if attr == 'class':
            cls = self.get_class_list()
            cls._append(self.classList)
            return cls.toString() if cls else None
        return super().getAttribute(attr)

    def addClass(self, *classes: str) -> None:
        """[Not Standard] Add classes to this node."""
        self.classList.add(*classes)

    def hasClass(self, class_: str) -> bool:  # noqa: D102
        """[Not Standard] Return if this node has ``class_`` class or not."""
        return class_ in self.classList

    def hasClasses(self) -> bool:  # noqa: D102
        """[Not Standard] Return if this node has any classes or not."""
        return len(self.classList) > 0

    def removeClass(self, *classes: str) -> None:
        """[Not Standard] Remove classes from this node."""
        _remove_cl = []
        for class_ in classes:
            if class_ not in self.classList:
                if class_ in self.get_class_list():
                    logger.warning(
                        'tried to remove class-level class: '
                        '{}'.format(class_)
                    )
                else:
                    logger.warning(
                        'tried to remove non-existing class: {}'.format(class_)
                    )
            else:
                _remove_cl.append(class_)
        self.classList.remove(*_remove_cl)

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

    def _get_child_html(self, child: Node) -> str:
        if isinstance(child, CharacterData):
            # temparary become new parent
            # text node needs to know its parent to escape or not its content
            self._append_child(child)
            html = child.html
            self._remove_child(child)
        else:
            html = getattr(child, 'html', str(child))
        return html

    def _append_child_web(self, child: 'WdomElement') -> Node:
        html = self._get_child_html(child)
        self.js_exec('insertAdjacentHTML', 'beforeend', html)
        return child

    def appendChild(self, child: 'WdomElement') -> Node:
        """Append child node at the last of child nodes.

        If this instance is connected to the node on browser, the child node is
        also added to it.
        """
        self._append_child_web(child)
        return self._append_child(child)

    def _insert_before_web(self, child: Node, ref_node: Node) -> Node:
        html = self._get_child_html(child)
        if isinstance(ref_node, WdomElement):
            ref_node.js_exec('insertAdjacentHTML', 'beforebegin', html)
        else:
            index = self.index(ref_node)
            self.js_exec('insert', index, html)
        return child

    def insertBefore(self, child: Node, ref_node: Node) -> Node:
        """Insert new child node before the reference child node.

        If the reference node is not a child of this node, raise ValueError. If
        this instance is connected to the node on browser, the child node is
        also added to it.
        """
        self._insert_before_web(child, ref_node)
        return self._insert_before(child, ref_node)

    def _remove_child_web(self, child: Node) -> Node:
        if child in self.childNodes:
            if isinstance(child, WdomElement):
                self.js_exec('removeChildById', child.rimo_id)
            else:
                self.js_exec('removeChildByIndex', self.index(child))
        return child

    def removeChild(self, child: Node) -> Node:
        """Remove the child node from this node.

        If the node is not a child of this node, raise ValueError.
        """
        self._remove_child_web(child)
        return self._remove_child(child)

    def _replace_child_web(self, new_child: Node, old_child: Node) -> None:
        html = self._get_child_html(new_child)
        if isinstance(old_child, WdomElement):
            self.js_exec('replaceChildById', html, old_child.rimo_id)
        elif old_child.parentNode is not None:
            # old_child will be Text Node
            index = old_child.parentNode.index(old_child)
            # Remove old_child before insert new child
            self._remove_child_web(old_child)
            self.js_exec('insert', index, html)

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
            msg = {'proto': '', 'type': 'click',
                   'currentTarget': {'id': self.rimo_id},
                   'target': {'id': self.rimo_id}}
            e = create_event(msg)
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

    def show(self) -> None:
        """[Not Standard] Show this node on browser."""
        self.hidden = False

    def hide(self) -> None:
        """[Not Standard] Hide this node on browser."""
        self.hidden = True
