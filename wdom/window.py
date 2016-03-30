#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.interface import Node
from wdom.element import Element


class CustomElementsRegistry(dict):
    def define(self, name:str, constructor:type, options:dict=None):
        tag = name.lower()
        self[tag] = constructor
        for elm in Element._elements:
            if not elm._registered and elm.tag == tag:
                elm.__class__ = constructor
                elm._registered = True


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
