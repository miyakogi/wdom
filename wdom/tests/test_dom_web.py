#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

import pytest
from tornado.web import Application
from selenium.common.exceptions import NoSuchElementException

from wdom.dom import Node, TextArea, Input, CheckBox
from wdom.view import get_document
from wdom.server import get_app
from wdom.misc import static_dir
from wdom.tests.util import WDTest
from wdom.tests.util import install_asyncio, start_browser, close_browser


def setup_module() -> None:
    install_asyncio()
    start_browser()


def teardown_module() -> None:
    close_browser()


class TestNode(WDTest):
    def setUp(self) -> None:
        self.document = get_document(autoreload=False)

        class Root(Node):
            tag = 'root'

        self.root = Root()
        self.document.set_body(self.root)
        self.app = get_app(self.document)
        self.app.add_favicon_path(static_dir)
        super().setUp()
        self.set_element(self.root)

    def get_app(self) -> Application:
        return self.app

    def test_node_text(self) -> None:
        assert self.get_text() == ''
        self.root.textContent = 'ROOT'
        assert self.get_text() == 'ROOT'

    def test_node_attr(self) -> None:
        assert self.get_attribute('src') is None
        self.root.setAttribute('src', 'a')
        assert self.get_attribute('src') == 'a'
        self.root.removeAttribute('src')
        assert self.get_attribute('src') is None

    def test_node_class(self) -> None:
        self.root.addClass('a')
        assert self.get_attribute('class') == 'a'

    def test_addremove_child(self) -> None:
        child = Node()
        self.root.appendChild(child)
        assert self.set_element_by_id(child.id) is True
        assert self.get_text() == ''
        child.textContent = 'Child'
        assert self.get_text() == 'Child'

        self.root.removeChild(child)
        with pytest.raises(NoSuchElementException):
            self.set_element_by_id(child.id)

    def test_replace_child(self) -> None:
        child1 = Node()
        child1.textContent = 'child1'
        child2 = Node()
        child2.textContent = 'child2'
        self.root.appendChild(child1)
        with pytest.raises(NoSuchElementException):
            self.set_element_by_id(child2.id)
        assert self.set_element_by_id(child1.id) is True
        assert self.get_text() == 'child1'

        self.root.replaceChild(child2, child1)
        with pytest.raises(NoSuchElementException):
            self.set_element_by_id(child1.id)
        assert self.set_element_by_id(child2.id) is True
        assert self.get_text() == 'child2'

    def test_showhide(self) -> None:
        self.root.textContent = 'root'
        assert self.is_displayed() is True
        self.root.hide()
        assert self.is_displayed() is False


class TestEvent(WDTest):
    def setUp(self) -> None:
        self.document = get_document(autoreload=False)
        self.root = Node()
        self.root.textContent = 'ROOT'
        self.click_mock = MagicMock()
        self.click_mock._is_coroutine = False
        self.root.addEventListener('click', self.click_mock)
        self.mock = MagicMock(self.root)
        self.mock.id = self.root.id
        self.mock.html = self.root.html

        self.document.set_body(self.mock)
        self.app = get_app(self.document)
        self.app.add_favicon_path(static_dir)
        super().setUp()

    def get_app(self) -> Application:
        return self.app

    def test_click(self) -> None:
        self.set_element(self.mock)
        self.click()
        self.wait(0.1)
        assert self.click_mock.call_count == 1
        self.mock.append.assert_not_called()
        self.mock.insert.assert_not_called()
        self.mock.remove.assert_not_called()
        self.mock.setAttribute.assert_not_called()
        self.mock.removeAttribute.assert_not_called()
        self.mock.appendChild.assert_not_called()
        self.mock.removeChild.assert_not_called()
        self.mock.replaceChild.assert_not_called()
        self.mock.addClass.assert_not_called()
        self.mock.removeClass.assert_not_called()


class TestInput(WDTest):
    def setUp(self) -> None:
        self.document = get_document(autoreload=False)
        self.root = Node()
        self.input = Input(parent=self.root)
        self.textarea = TextArea(parent=self.root)
        self.checkbox = CheckBox(parent=self.root)
        self.document.set_body(self.root)
        self.app = get_app(self.document)
        self.app.add_favicon_path(static_dir)
        super().setUp()

    def get_app(self) -> Application:
        return self.app

    def test_textinput(self) -> None:
        self.set_element(self.input)
        self.send_keys('abc')
        self.wait(0.02)
        assert self.input.value == 'abc'

        self.get(self.url)
        self.set_element(self.input)
        assert self.get_attribute('value') == 'abc'

        self.send_keys('def')
        self.wait(0.02)
        assert self.input.value == 'abcdef'

    def test_textarea(self) -> None:
        self.set_element(self.textarea)
        self.send_keys('abc')
        self.wait(0.02)
        assert self.textarea.value == 'abc'

        self.get(self.url)
        self.set_element(self.textarea)
        assert self.get_attribute('value') == 'abc'

        self.send_keys('def')
        self.wait(0.02)
        assert self.textarea.value == 'abcdef'

    def test_checkbox(self) -> None:
        self.set_element(self.checkbox)
        self.click()
        self.wait(0.02)
        assert self.checkbox.checked is True

        self.get(self.url)
        self.set_element(self.checkbox)
        assert self.get_attribute('checked') == 'true'

        self.click()
        self.wait(0.02)
        assert self.checkbox.checked is False
