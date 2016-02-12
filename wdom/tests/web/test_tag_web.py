#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

from tornado.web import Application
from selenium.common.exceptions import NoSuchElementException

from wdom.tag import Tag, TextArea, Input, CheckBox
from wdom.document import get_document
from wdom.server import get_app
from wdom.misc import static_dir, install_asyncio
from wdom.tests.web.remote_browser import WDTest


def setup_module():
    install_asyncio()


class TestNode(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)

        class Root(Tag):
            tag = 'root'

        self.root = Root()
        self.document.set_body(self.root)
        self.app = get_app(self.document)
        self.app.add_favicon_path(static_dir)
        super().setUp()
        self.set_element(self.root)

    def get_app(self) -> Application:
        return self.app

    def test_connection(self):
        self.assertIsTrue(self.root.connected)
        # this is an example, but valid domain for test
        self.get('http://example.com/')
        self.assertIsFalse(self.root.connected)

    def test_node_text(self):
        self.assertEqual(self.get_text(), '')
        self.root.textContent = 'ROOT'
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
        with self.assertRaises(NoSuchElementException):
            self.set_element_by_id(child2.id)
        self.assertIsTrue(self.set_element_by_id(child1.id))
        self.assertEqual(self.get_text(), 'child1')

        self.root.replaceChild(child2, child1)
        with self.assertRaises(NoSuchElementException):
            self.set_element_by_id(child1.id)
        self.assertIsTrue(self.set_element_by_id(child2.id))
        self.assertEqual(self.get_text(), 'child2')

    def test_showhide(self):
        self.root.textContent = 'root'
        self.assertIsTrue(self.is_displayed())
        self.root.hide()
        self.assertIsFalse(self.is_displayed())
        self.root.show()
        self.assertIsTrue(self.is_displayed())


class TestEvent(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)
        self.root = Tag()
        self.root.textContent = 'ROOT'
        self.click_mock = MagicMock()
        self.click_mock._is_coroutine = False
        self.root.addEventListener('click', self.click_mock)
        self.mock = MagicMock(self.root)
        self.mock.configure_mock(id=self.root.id, html=self.root.html,
                                 parentNode=None, nodeType=self.root.nodeType)

        self.document.set_body(self.mock)
        self.app = get_app(self.document)
        self.app.add_favicon_path(static_dir)
        super().setUp()

    def get_app(self) -> Application:
        return self.app

    def test_click(self):
        self.set_element(self.mock)
        self.click()
        self.wait(0.1)
        self.assertEqual(self.click_mock.call_count, 1)
        self.mock.append.assert_not_called()
        self.mock.remove.assert_not_called()
        self.mock.setAttribute.assert_not_called()
        self.mock.removeAttribute.assert_not_called()
        self.mock.appendChild.assert_not_called()
        self.mock.removeChild.assert_not_called()
        self.mock.replaceChild.assert_not_called()
        self.mock.addClass.assert_not_called()
        self.mock.removeClass.assert_not_called()


class TestInput(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)
        self.root = Tag()
        self.input = Input(parent=self.root)
        self.textarea = TextArea(parent=self.root)
        self.checkbox = CheckBox(parent=self.root)
        self.document.set_body(self.root)
        self.app = get_app(self.document)
        self.app.add_favicon_path(static_dir)
        super().setUp()

    def get_app(self) -> Application:
        return self.app

    def test_textinput(self):
        self.set_element(self.input)
        self.send_keys('abc')
        self.wait(0.02)
        self.assertEqual(self.input.value, 'abc')

        self.get(self.url)
        self.set_element(self.input)
        self.assertEqual(self.get_attribute('value'), 'abc')

        self.send_keys('def')
        self.wait(0.02)
        self.assertEqual(self.input.value, 'abcdef')

    def test_textarea(self):
        self.set_element(self.textarea)
        self.send_keys('abc')
        self.wait(0.02)
        self.assertEqual(self.textarea.value, 'abc')

        self.get(self.url)
        self.set_element(self.textarea)
        self.assertEqual(self.get_attribute('value'), 'abc')

        self.send_keys('def')
        self.wait(0.02)
        self.assertEqual(self.textarea.value, 'abcdef')

    def test_checkbox(self):
        self.set_element(self.checkbox)
        self.click()
        self.wait(0.02)
        self.assertIsTrue(self.checkbox.checked)

        self.get(self.url)
        self.set_element(self.checkbox)
        self.assertEqual(self.get_attribute('checked'), 'true')

        self.click()
        self.wait(0.02)
        self.assertIsFalse(self.checkbox.checked)
