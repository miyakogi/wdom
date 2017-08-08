#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Window and CustomElementsRegistry classes."""

from typing import Any, Dict, Type, TYPE_CHECKING

from wdom import server
from wdom.element import Element
from wdom.event import WebEventTarget
from wdom.node import Node
from wdom.tag import Tag, default_classes

if TYPE_CHECKING:
    from typing import Optional  # noqa: F401


class CustomElementsRegistry(dict):
    """Registry of registered custom elements.

    Keep custom elements by name (custom-tag or is-attr) and extended-tag
    (or None) pair.
    """

    def _upgrage_to_tag_class(self, elm: Node) -> None:
        if elm.type_ and 'type' not in elm.attributes:
            elm.setAttribute('type', elm.type_)
        if elm.is_ and 'is' not in elm.attributes:
            elm.setAttribute('is', elm.is_)

    def _upgrade_by_tag(self, name: str, constructor: type) -> None:
        for elm in Element._element_buffer:
            if not elm._registered and elm.tag == name:
                elm.__class__ = constructor
                elm._registered = True
                if isinstance(elm, Tag):
                    self._upgrage_to_tag_class(elm)

    def _upgrade_by_is(self, name: str, constructor: type, extends: str
                       ) -> None:
        for elm in Element._element_buffer:
            if (not elm._registered and elm.tag == extends and
                    elm.getAttribute('is') == name):
                elm.__class__ = constructor
                elm._registered = True
                if isinstance(elm, Tag):
                    self._upgrage_to_tag_class(elm)

    def _define(self, name: str, constructor: type,
                options: Dict[str, str] = None) -> None:
        extends = None  # Optional[str]
        if options:
            extends = options['extends'].lower()
        self[(name, extends)] = constructor
        if extends:
            self._upgrade_by_is(name, constructor, extends)
        else:
            self._upgrade_by_tag(name, constructor)

    def _define_orig(self, name: str, constructor: Type[Tag],
                     options: dict = None
                     ) -> None:
        self._define(name.lower(), constructor, options)

    def _define_class(self, constructor: Type[Tag]) -> None:
        is_ = getattr(constructor, 'is_', getattr(constructor, 'is', None))
        if is_:
            name = is_.lower()
            options = {'extends': constructor.tag}
        else:
            name = constructor.tag.lower()
            options = {}
        self._define(name, constructor, options)

    def define(self, *args: Any, **kwargs: Any) -> None:
        """Add new custom element."""
        if isinstance(args[0], str):
            self._define_orig(*args, **kwargs)
        elif isinstance(args[0], type):
            self._define_class(*args, **kwargs)
        else:
            raise TypeError(
                'Invalid argument for define: {}, {}'.format(args, kwargs))

    def _define_default(self) -> None:
        for cls in default_classes:
            self.define(cls)

    def reset(self) -> None:
        """Clear all registered custom elements."""
        self.clear()
        self._define_default()


customElements = CustomElementsRegistry()
customElements._define_default()


class Window(WebEventTarget):
    """Window base class."""

    @property
    def document(self) -> Node:
        """Return document object of this window."""
        return self._document

    @property
    def ownerDocument(self) -> Node:
        """Need for connection check."""
        return self.document

    @property
    def customElements(self) -> CustomElementsRegistry:
        """Return customElementsRegistry object."""
        return self._custom_elements

    @property
    def rimo_id(self) -> str:  # noqa: D102
        return 'window'

    @property
    def connected(self) -> bool:  # noqa: D102
        return server.is_connected()

    def __init__(self, document: Node) -> None:
        """Make new window object.

        :arg Document document: root document of the window.
        """
        super().__init__()
        self._document = document
        self._custom_elements = customElements
        self.addEventListener('mount', self._on_mount)
