#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from wdom.interface import Node
from wdom.element import Element
from wdom.tag import Tag


class ElementsDefineMap(defaultdict):
    def __init__(self):
        super().__init__(set)


class CustomElementsRegistry(dict):
    '''Keep elements by (name (custom-tag or is-attr), extended-tag (or None))
    pair.
    '''
    def _upgrage_to_tag_class(self, elm):
        if elm.type_ and 'type' not in elm.attributes:
            elm.setAttribute('type', elm.type_)
        if elm.is_ and 'is' not in elm.attributes:
            elm.setAttribute('is', elm.is_)

    def _upgrade_by_tag(self, name:str, constructor:type):
        for elm in Element._elements:
            if not elm._registered and elm.tag == name:
                elm.__class__ = constructor
                elm._registered = True
                if isinstance(elm, Tag):
                    self._upgrage_to_tag_class(elm)

    def _upgrade_by_is(self, name:str, constructor:type, extends:str):
        for elm in Element._elements:
            if (not elm._registered and elm.tag == extends and
                    elm.getAttribute('is') == name):
                elm.__class__ = constructor
                elm._registered = True
                if isinstance(elm, Tag):
                    self._upgrage_to_tag_class(elm)

    def define(self, name:str, constructor:type, options:dict=None):
        normalized_name = name.lower()
        extends = options.get('extends') if options else None
        self[(normalized_name, extends)] = constructor
        if extends:
            self._upgrade_by_is(normalized_name, constructor, extends)
        else:
            self._upgrade_by_tag(normalized_name, constructor)


customElements = CustomElementsRegistry()


class Window:
    @property
    def document(self) -> Node:
        return self._document

    @property
    def customElements(self) -> CustomElementsRegistry:
        return self._custom_elements

    def __init__(self, document:Node):
        self.connections = []
        self._document = document
        self._custom_elements = customElements
