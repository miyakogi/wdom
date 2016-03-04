#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

from selenium.common.exceptions import NoSuchElementException

from wdom.tag import Tag, TextArea, Input, CheckBox, Div
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.tests.web.remote_browser import WDTest
from wdom import aioserver


def setup_module():
    install_asyncio()


class TestNode(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)

        class Root(Tag):
            tag = 'root'

        self.root = Root()
        self.document.set_body(self.root)
        super().setUp()
        self.set_element(self.root)

    def test_connection(self):
        self.assertIsTrue(self.root.connected)
        # this is an example, but valid domain for test
        self.get('http://example.com/')
        self.assertIsFalse(self.root.connected)

    def test_node_text(self):
        self.assertEqual(self.get_text(), '')
        self.root.textContent = 'ROOT'
        self.wait()
        self.assertEqual(self.get_text(), 'ROOT')

    def test_node_attr(self):
        self.assertIsNone(self.get_attribute('src'))
        self.root.setAttribute('src', 'a')
        self.assertEqual(self.get_attribute('src'), 'a')
        self.root.removeAttribute('src')
        self.assertIsNone(self.get_attribute('src'))

    def test_node_class(self):
        self.root.addClass('a')
        self.assertEqual(self.get_attribute('class'), 'a')
        self.root.removeClass('a')
        self.assertEqual(self.get_attribute('class'), '')

    def test_addremove_child(self):
        child = Tag()
        self.root.appendChild(child)
        self.assertIsTrue(self.set_element_by_id(child.id))
        self.assertEqual(self.get_text(), '')
        child.textContent = 'Child'
        self.wait()
        self.assertEqual(self.get_text(), 'Child')

        self.root.removeChild(child)
        with self.assertRaises(NoSuchElementException):
            self.set_element_by_id(child.id)

    def test_replace_child(self):
        child1 = Tag()
        child1.textContent = 'child1'
        child2 = Tag()
        child2.textContent = 'child2'
        self.root.appendChild(child1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element_by_id(child2.id)
        self.assertIsTrue(self.set_element_by_id(child1.id))
        self.assertEqual(self.get_text(), 'child1')

        self.root.replaceChild(child2, child1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element_by_id(child1.id)
        self.assertIsTrue(self.set_element_by_id(child2.id))
        self.assertEqual(self.get_text(), 'child2')

    def test_showhide(self):
        self.root.textContent = 'root'
        self.wait()
        self.assertIsTrue(self.is_displayed())
        self.root.hide()
        self.wait()
        self.assertIsFalse(self.is_displayed())
        self.root.show()
        self.wait()
        self.assertIsTrue(self.is_displayed())


class TestEvent(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)
        self.root = Div('ROOT')
        self.click_mock = MagicMock()
        self.click_mock._is_coroutine = False
        self.root.addEventListener('click', self.click_mock)
        self.document.set_body(self.root)
        super().setUp()

    def test_click(self):
        self.set_element(self.root)
        self.click()
        self.wait()
        self.wait()
        self.wait()
        self.wait()
        self.wait()
        self.assertEqual(self.click_mock.call_count, 1)


class TestInput(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)
        self.root = Div()
        self.input = Input(parent=self.root)
        self.textarea = TextArea(parent=self.root)
        self.checkbox = CheckBox(parent=self.root)
        self.document.set_body(self.root)
        super().setUp()

    def test_textinput(self):
        self.set_element(self.input)
        self.send_keys('abc')
        self.wait()
        self.wait()
        self.wait()
        self.wait()
        self.wait()
        self.assertEqual(self.input.value, 'abc')

        self.get(self.url)
        self.set_element(self.input)
        self.assertEqual(self.get_attribute('value'), 'abc')

        self.send_keys('def')
        self.wait()
        self.wait()
        self.wait()
        self.wait()
        self.wait()
        self.assertEqual(self.input.value, 'abcdef')

    def test_textarea(self):
        self.set_element(self.textarea)
        self.send_keys('abc')
        self.wait()
        self.assertEqual(self.textarea.value, 'abc')

        self.get(self.url)
        self.set_element(self.textarea)
        self.assertEqual(self.get_attribute('value'), 'abc')

        self.send_keys('def')
        self.wait()
        self.assertEqual(self.textarea.value, 'abcdef')

    def test_checkbox(self):
        self.set_element(self.checkbox)
        self.click()
        self.wait()
        self.assertIsTrue(self.checkbox.checked)

        self.get(self.url)
        self.set_element(self.checkbox)
        self.assertEqual(self.get_attribute('checked'), 'true')

        self.wait()
        self.click()
        self.wait()
        self.assertEqual(self.get_attribute('checked'), None)
        self.assertIsFalse(self.checkbox.checked)


class TestNodeAIO(TestNode):
    module = aioserver
    wait_time = 0.05


class TestEventAIO(TestEvent):
    module = aioserver
    wait_time = 0.05


class TestInputAIO(TestInput):
    module = aioserver
    wait_time = 0.05
