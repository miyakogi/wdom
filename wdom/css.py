#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import OrderedDict
import logging
from typing import Optional

from wdom.interface import Node, WebIF

logger = logging.getLogger(__name__)
_css_norm_re = re.compile(r'([a-z])([A-Z])')
_style_cleanup_re = re.compile(r'\s*([:;])\s*', re.S)
_style_rule_re = re.compile(r'\s*(.*?)\s*{(.*?)}\s*', re.S)


def _lower_dash(m):
    return m.group(1) + '-' + m.group(2).lower()


def _normalize_css_property(prop):
    if prop == 'cssFloat':  # Special case
        return 'float'
    else:
        return _css_norm_re.sub(_lower_dash, prop)


class CSSStyleDeclaration(OrderedDict):
    def __init__(self, *args, parent=Optional['CSSRule'],
                 owner=Optional['Node'], **kwargs):
        self.parentRule = parent
        self._owner = owner
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

    def getPropertyValue(self, prop: str) -> str:
        return self.get(prop, '')

    def removeProperty(self, prop: str) -> str:
        return self.pop(prop, '')

    def setProperty(self, prop: str, value: str, priority=None):
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


def parse_style_decl(style: str, owner: Node = None) -> CSSStyleDeclaration:
    orig_style = style
    style_str = _style_cleanup_re.sub(r'\1', style.strip())
    if len(style_str) == 0:
        return CSSStyleDeclaration(owner=owner)

    style = CSSStyleDeclaration(owner=owner)
    for decls in style_str.split(';'):
        if ':' not in decls:
            if len(decls) > 0:
                logger.warning('[skip] unknown style: {}'.format(decls))
            continue
        decl_list = decls.split(':')
        if len(decl_list) != 2:
            raise ValueError(
                'Invalid style declaration: {0} in {1}'.format(
                    decls, orig_style))
        prop = decl_list[0]
        value = decl_list[1]
        style[prop] = value
    return style


class CSSStyleRule(object):
    def __init__(self, selector: str = '', style: CSSStyleDeclaration = None):
        self.selectorText = selector
        if style is None:
            self.style = CSSStyleDeclaration()
        else:
            self.style = style

    @property
    def cssText(self) -> str:
        _style = self.style.cssText
        if _style:
            return '{0} {{{1}}}'.format(self.selectorText, _style)
        else:
            return ''


class CSSRuleList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, kwargs)

    @property
    def length(self) -> int:
        return len(self)

    def item(self, index: int) -> CSSStyleRule:
        return self[index]

    @property
    def cssText(self) -> str:
        return '\n'.join(rule.cssText for rule in self)


def parse_style_rules(styles: str) -> CSSRuleList:
    rules = CSSRuleList()
    for m in _style_rule_re.finditer(styles):
        rules.append(CSSStyleRule(m.group(1), parse_style_decl(m.group(2))))
    return rules
