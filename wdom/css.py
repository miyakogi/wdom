#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSS related classes and functions."""

import re
from collections import OrderedDict
import logging
from typing import Any, Match

from wdom.node import AbstractNode

logger = logging.getLogger(__name__)
_css_norm_re = re.compile(r'([a-z])([A-Z])')
_style_cleanup_re = re.compile(r'\s*([:;])\s*', re.S)
_style_rule_re = re.compile(r'\s*(.*?)\s*{(.*?)}\s*', re.S)


def _lower_dash(m: Match) -> str:
    return m.group(1) + '-' + m.group(2).lower()


def _normalize_css_property(prop: str) -> str:
    if prop == 'cssFloat':  # Special case
        return 'float'
    return _css_norm_re.sub(_lower_dash, prop)


class CSSStyleDeclaration(OrderedDict):
    """Represents a CSS property-value pairs."""

    def __init__(self, style: str = None, parent: 'CSSStyleRule' = None,
                 owner: AbstractNode = None) -> None:
        """Initialize with styles.

        :arg str style: style strings.
        :arg CSSStyleRule parent: css style rule including this decl.
        :arg AbstractNode owner: owner node of this decl.
        """
        self.parentRule = parent
        self._owner = owner
        if style:
            self._parse_str(style)

    def _update_web(self) -> None:
        from wdom.web_node import WdomElement
        if isinstance(self._owner, WdomElement):
            css = self.cssText
            if css:
                self._owner.js_exec('setAttribute', 'style', css)
            else:
                self._owner.js_exec('removeAttribute', 'style')

    def _parse_str(self, style: str) -> None:
        self.clear()
        orig_style = style
        style_str = _style_cleanup_re.sub(r'\1', style.strip())
        if len(style_str) == 0:
            # do nothing, just clear and update
            self._update_web()
            return

        # temporary disable udpating browser for better performance
        self._owner, _owner = None, self._owner
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
            self[prop] = value
        self._owner = _owner
        self._update_web()

    @property
    def cssText(self) -> str:
        """String-representation."""
        text = '; '.join('{0}: {1}'.format(k, v) for k, v in self.items())
        if text:
            text += ';'
        return text

    @property
    def length(self) -> int:
        """Retrun number of included styles."""
        return len(self)

    @property
    def parentRule(self) -> 'CSSStyleRule':
        """Parent CSSStyleRule."""
        return self.__parent

    @parentRule.setter
    def parentRule(self, parent: 'CSSStyleRule') -> None:
        self.__parent = parent

    def getPropertyValue(self, prop: str) -> str:
        """Return value of the css property.

        If the property is not included, return empty string.
        """
        return self.get(prop, '')

    def removeProperty(self, prop: str) -> str:
        """Remove the css property."""
        removed_prop = self.get(prop)
        # removed_prop may be False or '', so need to check it is None
        if removed_prop is not None:
            del self[prop]
        return removed_prop

    def setProperty(self, prop: str, value: str, priority: str = None
                    ) -> None:
        """Set property as the value.

        The third argument ``priority`` is not implemented yet.
        """
        self[prop] = value

    def __getitem__(self, attr: str) -> str:
        return self.get(_normalize_css_property(attr), '')

    def __setitem__(self, attr: str, value: str) -> None:
        super().__setitem__(_normalize_css_property(attr), value)
        self._update_web()

    def __delitem__(self, attr: str) -> None:
        super().__delitem__(_normalize_css_property(attr))
        self._update_web()

    def __getattr__(self, attr: str) -> str:
        if attr.startswith('_') or attr in dir(self):
            return super().__getattr__(attr)  # type: ignore
        return self.get(_normalize_css_property(attr), '')

    def __setattr__(self, attr: str, value: str) -> None:
        if attr.startswith('_') or attr in dir(self):
            super().__setattr__(attr, value)
        else:
            self[_normalize_css_property(attr)] = value

    def __delattr__(self, attr: str) -> None:
        if attr.startswith('_') or attr in dir(self):
            super().__delattr__(attr)
        else:
            self.__delitem__(_normalize_css_property(attr))


def parse_style_decl(style: str, owner: AbstractNode = None
                     ) -> CSSStyleDeclaration:
    """Make CSSStyleDeclaration from style string.

    :arg AbstractNode owner: Owner of the style.
    """
    _style = CSSStyleDeclaration(style, owner=owner)
    return _style


class CSSStyleRule(object):
    """A single CSS style rule."""

    def __init__(self, selector: str = '', style: CSSStyleDeclaration = None
                 ) -> None:
        """Set selector text and related declaration."""
        self.selectorText = selector
        if style is None:
            self.style = CSSStyleDeclaration()
        else:
            self.style = style

    @property
    def cssText(self) -> str:
        """Return string representation of this rule."""
        _style = self.style.cssText
        if _style:
            return '{0} {{{1}}}'.format(self.selectorText, _style)
        return ''


class CSSRuleList(list):
    """List of CSSRule objects."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Make CSS rule list from css rules."""
        super().__init__(*args, **kwargs)

    @property
    def length(self) -> int:
        """Return Number of css rules included in this list."""
        return len(self)

    def item(self, index: int) -> CSSStyleRule:
        """Return the ``index``-th rule."""
        return self[index]

    @property
    def cssText(self) -> str:
        """Return string representation of this rule list."""
        return '\n'.join(rule.cssText for rule in self)


def parse_style_rules(styles: str) -> CSSRuleList:
    """Make CSSRuleList object from style string."""
    rules = CSSRuleList()
    for m in _style_rule_re.finditer(styles):
        rules.append(CSSStyleRule(m.group(1), parse_style_decl(m.group(2))))
    return rules
