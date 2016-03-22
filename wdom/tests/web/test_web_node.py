#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from unittest.mock import MagicMock

import pytest
from syncer import sync

from wdom.tests.util import TestCase
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.web_node import WebElement
from wdom.tests.web.remote_browser import WDTest, NoSuchElementException


def setup_module():
    install_asyncio()


class ElementTestCase(WDTest):
    def setUp(self):
        self.document = get_document(autoreload=False)
        self.document.set_body(self.get_elements())
        super().setUp()

    def get_elements(self):
        raise NotImplementedError


class WebElementTestCase(ElementTestCase):
    def get_elements(self):
        self.root = WebElement('div')
        self.tag = WebElement('span', parent=self.root)
        return self.root

    def test_connection(self):
        self.assertTrue(self.root.connected)
        self.get('http://example.com/')
        self.assertIsFalse(self.root.connected)

    def test_text_content(self):
        self.set_element(self.tag)
        self.assertEqual(self.get_text(), '')
        self.tag.textContent = 'text'
        self.wait()
        self.assertEqual(self.get_text(), 'text')

        child = WebElement('a')
        child.textContent = 'child'
        self.tag.appendChild(child)
        self.wait()
        self.assertEqual(self.get_text(), 'textchild')

        self.tag.textContent = 'NewText'
        self.wait()
        self.assertEqual(self.get_text(), 'NewText')
        with self.assertRaises(NoSuchElementException):
            self.set_element(child)

    def test_attr(self):
        self.set_element(self.tag)
        self.assertIsNone(self.get_attribute('src'))
        self.tag.setAttribute('src', 'a')
        self.assertEqual(self.get_attribute('src'), 'a')
        self.tag.removeAttribute('src')
        self.assertIsNone(self.get_attribute('src'))

    def test_addremove_child(self):
        child = WebElement('a')
        self.tag.appendChild(child)
        self.wait()
        self.assertIsTrue(self.set_element(child))
        self.assertEqual(self.get_text(), '')
        child.textContent = 'Child'
        self.wait()
        self.assertEqual(self.get_text(), 'Child')

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'Child')

        self.tag.removeChild(child)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(child)

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), '')

    def test_insert_child(self):
        self.set_element(self.tag)
        child1 = WebElement('a', parent=self.tag)
        child1.textContent = 'child1'
        child2 = WebElement('b')
        child2.textContent = 'child2'
        self.wait()

        self.assertIsTrue(self.set_element(child1))
        with self.assertRaises(NoSuchElementException):
            self.set_element(child2)

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'child1')

        self.tag.insertBefore(child2, child1)
        self.wait()
        self.assertIsTrue(self.set_element(child2))

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'child2child1')

        self.tag.empty()
        self.wait()
        self.assertEqual(self.get_text(), '')
        with self.assertRaises(NoSuchElementException):
            self.set_element(child1)
        with self.assertRaises(NoSuchElementException):
            self.set_element(child2)

    def test_replace_child(self):
        self.set_element(self.tag)
        child1 = WebElement('a')
        child1.textContent = 'child1'
        child2 = WebElement('b')
        child2.textContent = 'child2'
        self.tag.appendChild(child1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(child2)
        self.assertIsTrue(self.set_element(child1))
        self.assertEqual(self.get_text(), 'child1')

        self.tag.replaceChild(child2, child1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(child1)
        self.assertIsTrue(self.set_element(child2))
        self.assertEqual(self.get_text(), 'child2')
        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'child2')

    def test_shortcut_attr(self):
        self.tag.textContent = 'TAG'
        self.wait()
        self.set_element(self.tag)
        self.assertIsTrue(self.is_displayed())
        self.tag.hidden = True
        self.wait()
        self.assertIsFalse(self.is_displayed())
        self.tag.hidden = False
        self.wait()
        self.assertIsTrue(self.is_displayed())

    @sync
    async def test_get_rect(self):
        rect = WebElement('div', style='width:200px;height:100px;')
        self.tag.appendChild(rect)
        await asyncio.sleep(self.wait_time)

        data = await rect.getBoundingClientRect()
        self.assertEqual(data['width'], 200)
        self.assertEqual(data['height'], 100)

    @sync
    async def test_scroll(self):
        rect = WebElement('div',
                          style='width:3000px;height:3000px;background:#eee;')
        self.tag.appendChild(rect)
        await asyncio.sleep(self.wait_time)

        X = await rect.scrollX()
        Y = await rect.scrollY()
        self.assertEqual(X['x'], 0)
        self.assertEqual(Y['y'], 0)

        rect.scrollTo(200, 200)
        await asyncio.sleep(self.wait_time)
        X = await rect.scrollX()
        Y = await rect.scrollY()
        self.assertEqual(X['x'], 200)
        self.assertEqual(Y['y'], 200)


class EventTestCase(ElementTestCase):
    def get_elements(self):
        self.root = WebElement('div')
        self.tag = WebElement('span', parent=self.root)

        self.click_event_mock = MagicMock()
        self.click_event_mock._is_coroutine = False

        self.btn = WebElement('button')
        self.btn.textContent = 'click'
        self.btn.addEventListener('click', self.click_event_mock)

        self.input_event_mock = MagicMock()
        self.input_event_mock._is_coroutine = False

        self.input = WebElement('input', type='text')
        self.input.addEventListener('input', self.input_event_mock)

        self.root.appendChild(self.btn)
        self.root.appendChild(self.input)
        return self.root

    @pytest.mark.skipif(os.environ.get('TRAVIS', False),
                        reason='This test not pass only on travis')
    def test_click(self):
        self.set_element(self.btn)
        self.wait()
        self.click()
        self.wait()
        self.assertEqual(self.click_event_mock.call_count, 1)

    def test_input(self):
        self.set_element(self.input)
        self.wait()
        self.send_keys('abc')
        self.wait()
        self.assertEqual(self.input_event_mock.call_count, 3)


class TestWebElement(WebElementTestCase, TestCase):
    pass


class TestEvent(EventTestCase, TestCase):
    pass
