#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from wdom.tests.util import TestCase
from wdom.web_node import WebElement


class TestWebElementLocal(TestCase):
    def setUp(self):
        self.elm = WebElement('tag')
        self.c1 = WebElement()
        self.c2 = WebElement()

    def test_id(self):
        self.assertIsNotNone(re.match('<tag id="\d+"></tag>', self.elm.html))
        self.assertIsNotNone(re.match('\d+', self.elm.id))

    def test_noid(self):
        self.assertEqual('<tag></tag>', self.elm.html_noid)

        self.c1.tag = 'c1'
        appended_child1 = self.elm.appendChild(self.c1)
        self.assertIs(appended_child1, self.c1)
        self.assertEqual('<tag><c1></c1></tag>', self.elm.html_noid)

        self.c2.tag = 'c2'
        appended_child2 = self.c1.appendChild(self.c2)
        self.assertIs(appended_child2, self.c2)
        self.assertEqual('<tag><c1><c2></c2></c1></tag>', self.elm.html_noid)

    def test_id_init(self):
        elm = WebElement('tag', id='myid')
        self.assertEqual('<tag id="myid"></tag>', elm.html)

    def test_event(self):
        f = lambda data: None
        self.elm.addEventListener('click', f)
        self.assertIsNotNone(re.match(
            '<tag id="\d+" onclick="rimo.onclick\(this\);"></tag>',
            self.elm.html,
        ))

        self.elm.removeEventListener('click', f)
        self.assertIsNotNone(re.match('<tag id="\d+"></tag>', self.elm.html))

    def test_not_connected(self):
        self.assertFalse(self.elm.connected)

    def test_parent(self) -> None:
        self.assertIsNone(self.elm.parentNode)
        self.assertIsNone(self.c1.parentNode)
        self.elm.appendChild(self.c1)
        self.assertIs(self.elm, self.c1.parentNode)

        removed_child1 = self.elm.removeChild(self.c1)
        self.assertIs(removed_child1, self.c1)
        self.assertIsNone(self.c1.parentNode)

    def test_addremove_child(self):
        self.assertFalse(self.elm.hasChildNodes())
        self.elm.appendChild(self.c1)
        self.assertTrue(self.elm.hasChildNodes())
        self.assertIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.assertEqual(self.elm.length, 1)

        self.elm.appendChild(self.c2)
        self.assertIn(self.c1, self.elm)
        self.assertIn(self.c2, self.elm)
        self.assertEqual(self.elm.length, 2)
        self.c2.remove()
        self.assertEqual(self.elm.length, 1)
        self.assertIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.assertIsNone(self.c2.parentNode)

        self.elm.removeChild(self.c1)
        self.assertFalse(self.elm.hasChildNodes())
        self.assertEqual(self.elm.length, 0)
        self.assertNotIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)

        with self.assertRaises(ValueError):
            self.elm.removeChild(self.c1)

    def test_shallow_copy(self):
        from copy import copy
        clone = copy(self.elm)
        self.assertNotEqual(clone.id, self.elm.id)

        clone = self.elm.cloneNode()
        self.assertNotEqual(clone.id, self.elm.id)

    def test_deep_copy(self):
        from copy import deepcopy
        clone = deepcopy(self.elm)
        self.assertNotEqual(clone.id, self.elm.id)

        clone = self.elm.cloneNode(deep=True)
        self.assertNotEqual(clone.id, self.elm.id)
