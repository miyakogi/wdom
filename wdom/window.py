#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.interface import Node
from wdom.element import Element
from wdom.tag import Tag, default_classes


class CustomElementsRegistry(dict):
    '''Keep elements by (name (custom-tag or is-attr), extended-tag (or None))
    pair.
    '''
    def _upgrage_to_tag_class(self, elm):
        if elm.type_ and 'type' not in elm.attributes:
            elm.setAttribute('type', elm.type_)
        if elm.is_ and 'is' not in elm.attributes:
            elm.setAttribute('is', elm.is_)

    def _upgrade_by_tag(self, name: str, constructor: type):
        for elm in Element._elements:
            if not elm._registered and elm.tag == name:
                elm.__class__ = constructor
                elm._registered = True
                if isinstance(elm, Tag):
                    self._upgrage_to_tag_class(elm)

    def _upgrade_by_is(self, name: str, constructor: type, extends: str):
        for elm in Element._elements:
            if (not elm._registered and elm.tag == extends and
                    elm.getAttribute('is') == name):
                elm.__class__ = constructor
                elm._registered = True
                if isinstance(elm, Tag):
                    self._upgrage_to_tag_class(elm)

    def _define(self, name: str, constructor: type, options: dict = None):
        extends = options.get('extends').lower() if options else None
        self[(name, extends)] = constructor
        if extends:
            self._upgrade_by_is(name, constructor, extends)
        else:
            self._upgrade_by_tag(name, constructor)

    def _define_orig(self, name: str, constructor: type, options: dict = None):
        self._define(name.lower(), constructor, options)

    def _define_class(self, constructor: type):
        is_ = getattr(constructor, 'is_', getattr(constructor, 'is', None))
        if is_:
            name = is_.lower()
            options = {'extends': constructor.tag}
        else:
            name = constructor.tag.lower()
            options = {}
        self._define(name, constructor, options)

    def define(self, *args, **kwargs):
        if isinstance(args[0], str):
            self._define_orig(*args, **kwargs)
        elif isinstance(args[0], type):
            self._define_class(*args, **kwargs)
        else:
            raise TypeError(
                'Invalid argument for define: {}, {}'.format(args, kwargs))

    def _define_default(self):
        for cls in default_classes:
            self.define(cls)

    def reset(self):
        self.clear()
        self._define_default()


customElements = CustomElementsRegistry()
customElements._define_default()


class Window:
    @property
    def document(self) -> Node:
        return self._document

    @property
    def customElements(self) -> CustomElementsRegistry:
        return self._custom_elements

    def __init__(self, document: Node):
        self._document = document
        self._custom_elements = customElements
