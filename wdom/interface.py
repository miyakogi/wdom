#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom import Node

__all__ = ('Event', 'Node', 'NodeList', 'HTMLCollection')


class Event:
    def __init__(self, type: str, **kwargs):
        self.type = type.lower()
        self.__dict__.update(kwargs)

    def stopPrapagation(self):
        raise NotImplementedError


class NodeList:
    def __init__(self, ref: list):
        self.ref = ref

    def __getitem__(self, index: int) -> Node:
        return self.ref[index]

    def __len__(self) -> int:
        return len(self.ref)

    def __contains__(self, other: Node) -> bool:
        return other in self.ref

    def __iter__(self) -> Node:
        for n in self.ref:
            yield n

    @property
    def length(self) -> int:
        return len(self)

    def item(self, index: int) -> Node:
        '''Return item with the index. If the index is negative number or out
        of the list, return None.
        '''
        if not isinstance(index, int):
            raise TypeError(
                'Indeces must be integer, not {}'.format(type(index)))
        return self.ref[index] if 0 <= index < self.length else None

    def index(self, node: Node) -> int:
        '''Get index of the node.'''
        return self.ref.index(node)


class HTMLCollection(NodeList):
    def namedItem(self, name: str) -> Node:
        for n in self.ref:
            if n.getAttribute('id') == name:
                return n
        for n in self.ref:
            if n.getAttribute('name') == name:
                return n
