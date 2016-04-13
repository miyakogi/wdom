#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

from selenium.common.exceptions import NoSuchElementException

from wdom.tag import Tag, Textarea, Input, CheckBox, Div
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.testing import RemoteBrowserTestCase, TestCase
from wdom import server


def setUpModule():
    install_asyncio()


class NodeTestCase(RemoteBrowserTestCase):
    def setUp(self):
        self.document = get_document(autoreload=False)

        class Root(Tag):
            tag = 'root'

        self.root = Root()
        self.document.body.prepend(self.root)
        super().setUp()
        self.set_element(self.root)

    def test_connection(self):
        self.assertIsTrue(self.root.connected)
        # this is an example, but valid domain for test
        self.browser.get('http://example.com/')
        self.assertIsFalse(self.root.connected)

    def test_node_text(self):
        self.assertEqual(self.browser.get_text(), '')
        self.root.textContent = 'ROOT'
        self.wait()
        self.assertEqual(self.browser.get_text(), 'ROOT')

    def test_node_attr(self):
        self.assertIsNone(self.browser.get_attribute('src'))
        self.root.setAttribute('src', 'a')
        self.wait()
        self.assertEqual(self.browser.get_attribute('src'), 'a')
        self.root.removeAttribute('src')
        self.wait()
        self.assertIsNone(self.browser.get_attribute('src'))

    def test_node_class(self):
        self.root.addClass('a')
        self.wait()
        self.assertEqual(self.browser.get_attribute('class'), 'a')
        self.root.removeClass('a')
        self.wait()
        self.assertEqual(self.browser.get_attribute('class'), '')

    def test_addremove_child(self):
        child = Tag()
        self.root.appendChild(child)
        self.wait()
        self.assertIsTrue(self.set_element(child))
        self.assertEqual(self.browser.get_text(), '')
        child.textContent = 'Child'
        self.wait()
        self.assertEqual(self.browser.get_text(), 'Child')

        self.root.removeChild(child)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(child)

    def test_replace_child(self):
        child1 = Tag()
        child1.textContent = 'child1'
        child2 = Tag()
        child2.textContent = 'child2'
        self.root.appendChild(child1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(child2)
        self.assertIsTrue(self.set_element(child1))
        self.assertEqual(self.browser.get_text(), 'child1')

        self.root.replaceChild(child2, child1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(child1)
        self.assertIsTrue(self.set_element(child2))
        self.assertEqual(self.browser.get_text(), 'child2')

    def test_showhide(self):
        self.root.textContent = 'root'
        self.wait()
        self.assertIsTrue(self.browser.is_displayed())
        self.root.hide()
        self.wait()
        self.assertIsFalse(self.browser.is_displayed())
        self.root.show()
        self.wait()
        self.assertIsTrue(self.browser.is_displayed())


class InputTestCase(RemoteBrowserTestCase):
    def setUp(self):
        self.document = get_document(autoreload=False)
        self.root = Div()
        self.input = Input(parent=self.root, type='text')
        self.textarea = Textarea(parent=self.root)
        self.checkbox = CheckBox(parent=self.root)
        self.document.body.prepend(self.root)
        super().setUp()

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                        reason='This test not pass only on travis')
    def test_textinput(self):
        self.set_element(self.input)
        self.wait()
        self.browser.send_keys('abc')
        self.wait()
        self.assertEqual(self.input.value, 'abc')

        self.browser.get(self.url)
        self.set_element(self.input)
        self.assertEqual(self.browser.get_attribute('value'), 'abc')

        self.browser.send_keys('def')
        self.wait()
        self.assertEqual(self.input.value, 'abcdef')

    def test_textarea(self):
        self.set_element(self.textarea)
        self.browser.send_keys('abc')
        self.wait()
        self.assertEqual(self.textarea.value, 'abc')

        self.browser.get(self.url)
        self.set_element(self.textarea)
        self.assertEqual(self.browser.get_attribute('value'), 'abc')

        self.browser.send_keys('def')
        self.wait()
        self.assertEqual(self.textarea.value, 'abcdef')

    def test_checkbox(self):
        self.set_element(self.checkbox)
        self.browser.click()
        self.wait()
        self.assertIsTrue(self.checkbox.checked)

        self.browser.get(self.url)
        self.set_element(self.checkbox)
        self.assertEqual(self.browser.get_attribute('checked'), 'true')

        self.wait()
        self.browser.click()
        self.wait()
        self.assertEqual(self.browser.get_attribute('checked'), None)
        self.assertIsFalse(self.checkbox.checked)


class TestNode(NodeTestCase, TestCase):
    module = server


class TestInput(InputTestCase, TestCase):
    module = server
