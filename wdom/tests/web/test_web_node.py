#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import unittest
from unittest.mock import MagicMock

from syncer import sync

from wdom.tests.util import TestCase
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.node import DocumentFragment
from wdom.web_node import WebElement
from wdom.tests.web.remote_browser import WDTest, NoSuchElementException


def setUpModule():
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
        self.df = DocumentFragment()
        self.c1 = WebElement('c1')
        self.c2 = WebElement('c2')
        self.c3 = WebElement('c3')
        self.c4 = WebElement('c4')
        self.c1.textContent = 'child1'
        self.c2.textContent = 'child2'
        self.c3.textContent = 'child3'
        self.c4.textContent = 'child4'
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

        self.c1.textContent = 'child'
        self.tag.appendChild(self.c1)
        self.wait()
        self.assertEqual(self.get_text(), 'textchild')

        self.tag.textContent = 'NewText'
        self.wait()
        self.assertEqual(self.get_text(), 'NewText')
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c1)

    def test_attr(self):
        self.set_element(self.tag)
        self.assertIsNone(self.get_attribute('src'))
        self.tag.setAttribute('src', 'a')
        self.wait()
        self.assertEqual(self.get_attribute('src'), 'a')
        self.tag.removeAttribute('src')
        self.wait()
        self.assertIsNone(self.get_attribute('src'))

    def test_addremove_child(self):
        self.tag.appendChild(self.c1)
        self.wait()
        self.assertIsTrue(self.set_element(self.c1))
        self.assertEqual(self.get_text(), 'child1')
        self.c1.textContent = 'Child'
        self.wait()
        self.assertEqual(self.get_text(), 'Child')

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'Child')

        self.tag.removeChild(self.c1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c1)

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), '')

    def test_insert_child(self):
        self.set_element(self.tag)
        # test parent in constructor
        self.c1 = WebElement('c1', parent=self.tag)
        self.c1.textContent = 'child1'
        self.wait(0.1)

        self.assertIsTrue(self.set_element(self.c1))
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c2)

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'child1')

        self.tag.insertBefore(self.c2, self.c1)
        self.wait(0.1)
        self.assertIsTrue(self.set_element(self.c2))

        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'child2child1')

        self.tag.empty()
        self.wait(0.1)
        self.assertEqual(self.get_text(), '')
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c1)
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c2)

    def test_add_df(self):
        self.set_element(self.tag)
        self.df.append(self.c1, self.c2, 'text')
        self.tag.appendChild(self.df)
        self.wait()
        self.assertEqual(self.get_text(), 'child1child2text')

        df = DocumentFragment()
        df.append(self.c3, 'text2')
        self.tag.appendChild(df)
        self.wait()
        self.assertEqual(self.get_text(), 'child1child2textchild3text2')

    def test_insert_df(self):
        self.set_element(self.tag)
        self.tag.appendChild(self.c1)
        self.df.append(self.c2, self.c3, 'text')
        self.tag.insertBefore(self.df, self.c1)
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'child2child3textchild1')

        df = DocumentFragment()
        df.append(self.c4, 'text2')
        self.tag.insertBefore(df, self.c3)
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'child2child4text2child3textchild1')

    def test_replace_child(self):
        self.set_element(self.tag)
        self.tag.appendChild(self.c1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c2)
        self.assertIsTrue(self.set_element(self.c1))
        self.assertEqual(self.get_text(), 'child1')

        self.tag.replaceChild(self.c2, self.c1)
        self.wait()
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c1)
        self.assertIsTrue(self.set_element(self.c2))
        self.assertEqual(self.get_text(), 'child2')
        self.set_element(self.tag)
        self.assertEqual(self.get_text(), 'child2')

    def test_append(self):
        self.set_element(self.tag)
        self.tag.append(self.c1)
        self.wait()
        self.assertEqual(self.get_text(), 'child1')

        self.tag.append(self.c2, self.c3)
        self.wait()
        self.assertEqual(self.get_text(), 'child1child2child3')

        self.tag.append(self.c4, self.c1)
        self.wait()
        self.assertEqual(self.get_text(), 'child2child3child4child1')

        self.tag.append('t1', 't2')
        self.wait()
        self.assertEqual(self.get_text(), 'child2child3child4child1t1t2')

    def test_prepend(self):
        self.set_element(self.tag)
        self.tag.prepend(self.c1)
        self.wait()
        self.assertEqual(self.get_text(), 'child1')

        self.tag.prepend(self.c2, self.c3)
        self.wait()
        self.assertEqual(self.get_text(), 'child2child3child1')

        self.tag.prepend(self.c4, self.c1)
        self.wait()
        self.assertEqual(self.get_text(), 'child4child1child2child3')

        self.tag.prepend('t1', 't2')
        self.wait()
        self.assertEqual(self.get_text(), 't1t2child4child1child2child3')

    def test_prepend_append_text(self):
        self.set_element(self.tag)
        self.tag.append('t1')
        self.wait()
        self.assertEqual(self.get_text(), 't1')

        self.tag.firstChild.remove()
        self.wait()
        self.assertEqual(self.get_text(), '')

        self.tag.prepend('t2')
        self.wait()
        self.assertEqual(self.get_text(), 't2')

        self.tag.append('t3', 't4')
        self.wait()
        self.assertEqual(self.get_text(), 't2t3t4')

        self.tag.prepend('t5', 't6')
        self.wait()
        self.assertEqual(self.get_text(), 't5t6t2t3t4')

    def test_after(self):
        self.set_element(self.tag)
        self.tag.append(self.c1)
        self.c1.after(self.c2)
        self.wait()
        self.assertEqual(self.get_text(), 'child1child2')

        self.c1.after(self.c3, self.c4)
        self.wait()
        self.assertEqual(self.get_text(), 'child1child3child4child2')

        self.c1.after(self.c2, 'text')
        self.wait()
        self.assertEqual(self.get_text(), 'child1child2textchild3child4')

    def test_before(self):
        self.set_element(self.tag)
        self.tag.append(self.c1)
        self.c1.before(self.c2)
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'child2child1')

        self.c1.before(self.c3, self.c4)
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'child2child3child4child1')

        self.c1.before(self.c2, 'text')
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'child3child4child2textchild1')

    def test_after_before_text(self):
        self.set_element(self.tag)
        self.tag.append('a')
        t = self.tag.firstChild
        t.after('b')
        self.wait()
        self.assertEqual(self.get_text(), 'ab')

        t.after('c', 'd')
        self.wait()
        self.assertEqual(self.get_text(), 'acdb')

        t.before('e')
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'eacdb')

        t.before('f', 'g')
        self.wait(0.1)
        self.assertEqual(self.get_text(), 'efgacdb')

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

    def test_style(self):
        self.tag.textContent = 'Style'
        self.wait()
        self.set_element(self.tag)
        self.assertEqual(self.get_attribute('style'), '')
        style = 'color: red;'
        self.tag.style = style
        self.wait()
        self.assertEqual(self.get_attribute('style'), style)
        self.tag.style.color = 'black'
        self.wait()
        self.assertEqual(self.get_attribute('style'), 'color: black;')

    def test_classlist(self):
        self.set_element(self.tag)
        self.assertEqual(self.get_attribute('class'), '')
        self.tag.classList.add('a')
        self.wait()
        self.assertEqual(self.get_attribute('class'), 'a')
        self.tag.classList.add('b', 'c', 'd')
        self.wait()
        self.assertEqual(self.get_attribute('class'), 'a b c d')

        self.tag.classList.remove('c')
        self.wait()
        self.assertEqual(self.get_attribute('class'), 'a b d')
        self.tag.classList.remove('a', 'd')
        self.wait()
        self.assertEqual(self.get_attribute('class'), 'b')

        self.tag.classList.toggle('b')
        self.wait()
        self.assertEqual(self.get_attribute('class'), '')
        self.tag.classList.toggle('b')
        self.wait()
        self.assertEqual(self.get_attribute('class'), 'b')

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

    @unittest.skipIf(os.environ.get('TRAVIS', False),
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
