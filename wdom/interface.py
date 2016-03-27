#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom import Node

__all__ = ('Event', 'Node')


class Event:
    def __init__(self, type:str, **kwargs):
        self.type = type
        self.__dict__.update(kwargs)

    def stopPrapagation(self):
        raise NotImplementedError
