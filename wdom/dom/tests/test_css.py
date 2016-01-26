#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase

import pytest

from wdom.dom.css import _normalize_css_property
from wdom.dom.css import CSSStyleDeclaration, parse_style_decl
from wdom.dom.css import CSSStyleRule
from wdom.dom.css import CSSRuleList


@pytest.mark.parametrize(
    'input,expect', [
        ('color', 'color'),
        ('fontColor', 'font-color'),
        ('borderWidth', 'border-width'),
        ('borderBottomColor', 'border-bottom-color'),
        ('zIndex', 'z-index'),
        ('cssFloat', 'float'),
    ])
def test_normalize(input, expect):
    assert _normalize_css_property(input) == expect


class TestCSSStyleDeclaration(TestCase):
    def setUp(self):
        self.css = CSSStyleDeclaration()

    def test_init(self):
        self.assertEqual(self.css.cssText, '')
        self.assertEqual(self.css.length, 0)

    def test_set_get_remove(self):
        self.assertEqual(self.css.getPropertyValue('color'), '')

        self.css.setProperty('color', 'red')
        self.assertEqual(self.css.getPropertyValue('color'), 'red')
        self.assertEqual(self.css['color'], 'red')
        self.assertEqual(self.css.cssText, 'color: red;')
        self.assertEqual(self.css.length, 1)

        self.css.setProperty('font-color', '#000')
        self.assertEqual(self.css.getPropertyValue('color'), 'red')
        self.assertEqual(self.css['color'], 'red')
        self.assertEqual(self.css.getPropertyValue('font-color'), '#000')
        self.assertEqual(self.css['font-color'], '#000')
        self.assertIn('font-color: #000;', self.css.cssText)
        self.assertIn('color: red;', self.css.cssText)
        self.assertEqual(self.css.length, 2)

        # removedProperty returns value of removed property
        self.assertEqual(self.css.removeProperty('color'), 'red')

        self.assertEqual(self.css.getPropertyValue('color'), '')
        self.assertEqual(self.css['color'], '')
        self.assertEqual(self.css.getPropertyValue('font-color'), '#000')
        self.assertEqual(self.css['font-color'], '#000')
        self.assertEqual(self.css.cssText, 'font-color: #000;')
        self.assertNotIn('color: red;', self.css.cssText)
        self.assertEqual(self.css.length, 1)

    def test_property_access(self):
        self.assertEqual(self.css.color, '')
        self.css.color = 'red'
        self.assertEqual(self.css.color, 'red')
        self.assertEqual(self.css.getPropertyValue('color'), 'red')
        self.assertEqual(self.css['color'], 'red')
        self.assertEqual(self.css.cssText, 'color: red;')
        self.assertEqual(self.css.length, 1)

        del self.css.color
        self.assertEqual(self.css.color, '')
        self.assertEqual(self.css.getPropertyValue('color'), '')
        self.assertEqual(self.css.cssText, '')
        self.assertEqual(self.css.length, 0)

    def test_property_access_dash(self):
        self.assertEqual(self.css.zIndex, '')
        self.assertEqual(self.css.getPropertyValue('z-index'), '')
        self.assertEqual(self.css.getPropertyValue('zIndex'), '')

        self.css.zIndex = 1
        self.assertEqual(self.css.zIndex, 1)
        self.assertEqual(self.css.getPropertyValue('z-index'), 1)
        self.assertEqual(self.css.getPropertyValue('zIndex'), '')
        self.assertEqual(self.css.cssText, 'z-index: 1;')
        self.assertEqual(self.css.length, 1)

        self.css.setProperty('z-index', 2)
        self.assertEqual(self.css.zIndex, 2)
        self.assertEqual(self.css.getPropertyValue('z-index'), 2)
        self.assertEqual(self.css.getPropertyValue('zIndex'), '')
        self.assertEqual(self.css.cssText, 'z-index: 2;')
        self.assertEqual(self.css.length, 1)

        del self.css.zIndex
        self.assertEqual(self.css.zIndex, '')
        self.assertEqual(self.css.getPropertyValue('z-index'), '')
        self.assertEqual(self.css.getPropertyValue('zIndex'), '')
        self.assertEqual(self.css.cssText, '')
        self.assertEqual(self.css.length, 0)

    def test_property_access_dash_two(self):
        self.assertEqual(self.css.listStyleType, '')
        self.assertEqual(self.css.getPropertyValue('list-style-type'), '')
        self.assertEqual(self.css.getPropertyValue('listStyleType'), '')

        self.css.listStyleType = 'disc'
        self.assertEqual(self.css.listStyleType, 'disc')
        self.assertEqual(self.css.getPropertyValue('list-style-type'), 'disc')
        self.assertEqual(self.css.getPropertyValue('listStyleType'), '')
        self.assertEqual(self.css.cssText, 'list-style-type: disc;')
        self.assertEqual(self.css.length, 1)

        del self.css.listStyleType
        self.assertEqual(self.css.listStyleType, '')
        self.assertEqual(self.css.getPropertyValue('list-style-type'), '')
        self.assertEqual(self.css.getPropertyValue('listStyleType'), '')
        self.assertEqual(self.css.cssText, '')
        self.assertEqual(self.css.length, 0)

    def test_float(self):
        self.assertEqual(self.css.cssFloat, '')
        self.assertEqual(self.css.getPropertyValue('float'), '')
        self.assertEqual(self.css.getPropertyValue('cssFloat'), '')
        self.assertEqual(self.css.getPropertyValue('css-float'), '')

        self.css.cssFloat = 1
        self.assertEqual(self.css.getPropertyValue('cssFloat'), '')
        self.assertEqual(self.css.getPropertyValue('float'), 1)
        self.assertEqual(self.css.getPropertyValue('css-float'), '')


@pytest.mark.parametrize('style,parsed',[
    ('color:red;', 'color: red;'),
    ('color  :red  ;', 'color: red;'),
    ('margin: 1 3 4 5;', 'margin: 1 3 4 5;'),
    (' margin :1 3 4 5   ;  ', 'margin: 1 3 4 5;'),
    ('z-index: 1;', 'z-index: 1;'),
])
def test_parse_style_decl(style, parsed):
    assert parse_style_decl(style).cssText == parsed


class TestCSSStyleRule(TestCase):
    def setUp(self):
        self.rule = CSSStyleRule()

    def test_blank(self):
        self.assertEqual(self.rule.cssText, '')
        self.rule.selectorText = 'h1'
        self.assertEqual(self.rule.cssText, '')

    def test_init(self):
        style = CSSStyleDeclaration()
        style.color = 'red'
        rule = CSSStyleRule('h1', style)
        self.assertEqual(rule.cssText, 'h1 {color: red;}')

    def test_overwrite_style(self):
        self.rule.style = CSSStyleDeclaration()
        self.rule.style.color = 'red'
        self.assertEqual(self.rule.cssText, ' {color: red;}')

        self.rule.selectorText = 'h1'
        self.assertEqual(self.rule.cssText, 'h1 {color: red;}')

        self.rule.selectorText = 'h1,h2'
        self.assertEqual(self.rule.cssText, 'h1,h2 {color: red;}')

        self.rule.style.removeProperty('color')
        self.assertEqual(self.rule.cssText, '')


class TestCSSRuleList(TestCase):
    def setUp(self):
        self.list = CSSRuleList()
        self.style = CSSStyleDeclaration()
        self.style.color = 'red'
        self.rule = CSSStyleRule('h1', self.style)

    def test_blank(self):
        self.assertEqual(self.list.cssText, '')

    def test_append(self):
        self.list.append(self.rule)
        self.assertEqual(self.list.cssText, 'h1 {color: red;}')

    def test_append2(self):
        self.list.append(self.rule)
        rule2 = CSSStyleRule('h2', CSSStyleDeclaration(background='black'))
        self.list.append(rule2)
        self.assertEqual(
            self.list.cssText, 'h1 {color: red;}\nh2 {background: black;}')
