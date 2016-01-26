#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

_css_norm_re = re.compile(r'([a-z])([A-Z])')


def _lower_dash(m):
    return m.group(1) + '-' + m.group(2).lower()


def _normalize_css_property(prop):
    if prop == 'cssFloat':  # Special case
        return 'float'
    else:
        return _css_norm_re.sub(_lower_dash, prop)


class CSSStyleDeclaration(dict):
    def __init__(self, *args, parent=None, **kwargs):
        self.parentRule = parent
        super().__init__(*args, **kwargs)

    @property
    def cssText(self) -> str:
        text = '; '.join('{0}: {1}'.format(k, v) for k, v in self.items())
        if text:
            text += ';'
        return text

    @property
    def length(self) -> int:
        return len(self)

    @property
    def parentRule(self):
        return self._parent

    @parentRule.setter
    def parentRule(self, parent):
        self._parent = parent

    def getPropertyValue(self, prop:str) -> str:
        return self.get(prop, '')

    def removeProperty(self, prop:str) -> str:
        return self.pop(prop, '')

    def setProperty(self, prop:str, value:str, priority=None):
        self[prop] = value

    def __getitem__(self, attr) -> str:
        return self.get(_normalize_css_property(attr), '')

    def __setitem__(self, attr, value) -> str:
        super().__setitem__(_normalize_css_property(attr), value)

    def __delitem__(self, attr):
        super().__delitem__(_normalize_css_property(attr))

    def __getattr__(self, attr: str) -> str:
        if attr.startswith('_') or attr in dir(self):
            return super().__getattr__(attr)
        else:
            return self.get(_normalize_css_property(attr), '')

    def __setattr__(self, attr, value):
        if attr.startswith('_') or attr in dir(self):
            super().__setattr__(attr, value)
        else:
            self[_normalize_css_property(attr)] = value

    def __delattr__(self, attr):
        if attr.startswith('_') or attr in dir(self):
            super().__delattr__(attr)
        else:
            self.__delitem__(_normalize_css_property(attr))
