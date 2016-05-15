#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import asyncio
import unittest
from unittest.mock import MagicMock

from syncer import sync

from wdom.testing import TestCase
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.node import DocumentFragment, Text
from wdom.web_node import WebElement
from wdom.testing import RemoteBrowserTestCase, NoSuchElementException
from wdom.testing import start_remote_browser, close_remote_browser


def setUpModule():
    install_asyncio()
    start_remote_browser()


def tearDownModule():
    close_remote_browser()


class ElementTestCase(RemoteBrowserTestCase):
    if os.environ.get('TRAVIS', False):
        wait_time = 0.1

    def setUp(self):
        super().setUp()
        self.document = get_document()
        self.document.body.prepend(self.get_elements())
        self.start()

    def get_elements(self):
        raise NotImplementedError


class TestWebElement(ElementTestCase, TestCase):
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
        self.wait_until(lambda: self.root.connected)
        self.assertTrue(self.root.connected)
        self.browser.get('http://example.com/')
        self.assertIsFalse(self.root.connected)

    def test_text_content(self):
        self.set_element(self.tag)
        self.assertEqual(self.element.text, '')
        self.tag.textContent = 'text'
        self.wait_until(lambda: self.element.text == 'text')
        self.assertEqual(self.element.text, 'text')

        self.c1.textContent = 'child'
        self.tag.appendChild(self.c1)
        self.wait_until(lambda: self.element.text == 'textchild')
        self.assertEqual(self.element.text, 'textchild')

        self.tag.textContent = 'NewText'
        self.wait_until(lambda: self.element.text == 'NewText')
        self.assertEqual(self.element.text, 'NewText')
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c1, self.wait_time * 10)

        self.set_element(self.tag)
        t_node = Text('TextNode')
        self.tag.replaceChild(t_node, self.tag.childNodes[0])
        self.wait_until(lambda: self.element.text == 'TextNode')
        self.assertEqual(self.element.text, 'TextNode')

        self.tag.removeChild(self.tag.childNodes[0])
        self.set_element(self.tag)
        self.wait_until(lambda: self.element.text == '')
        self.assertEqual(self.element.text, '')

    def test_attr(self):
        self.set_element(self.tag)
        self.assertIsNone(self.element.get_attribute('src'))
        self.tag.setAttribute('src', 'a')
        self.wait_until(lambda: self.element.get_attribute('src') == 'a')
        self.assertEqual(self.element.get_attribute('src'), 'a')
        self.tag.removeAttribute('src')
        self.wait_until(lambda: self.element.get_attribute('src') is None)
        self.assertIsNone(self.element.get_attribute('src'))

    def test_addremove_child(self):
        self.tag.appendChild(self.c1)
        self.set_element(self.c1)
        self.assertEqual(self.element.text, 'child1')
        self.c1.textContent = 'Child'
        self.wait_until(lambda: self.element.text == 'Child')
        self.assertEqual(self.element.text, 'Child')

        self.set_element(self.tag)
        self.wait_until(lambda: self.element.text == 'Child')
        self.assertEqual(self.element.text, 'Child')

        self.tag.removeChild(self.c1)
        with self.assertRaises(NoSuchElementException):
            self.wait(0.1)
            self.set_element(self.c1, self.wait_time * 10)

        self.set_element(self.tag)
        self.wait_until(lambda: self.element.text == '')
        self.assertEqual(self.element.text, '')

    def test_insert_child(self):
        self.set_element(self.tag)
        # test parent in constructor
        self.c1 = WebElement('c1', parent=self.tag)
        self.c1.textContent = 'child1'

        self.assertIsTrue(self.set_element(self.c1))
        with self.assertRaises(NoSuchElementException):
            self.wait(0.1)
            self.set_element(self.c2, self.wait_time * 10)

        self.set_element(self.tag)
        self.wait_until(lambda: self.element.text == 'child1')
        self.assertEqual(self.element.text, 'child1')

        self.tag.insertBefore(self.c2, self.c1)
        self.assertIsTrue(self.set_element(self.c2))

        self.set_element(self.tag)
        self.wait_until(lambda: self.element.text == 'child2child1')
        self.assertEqual(self.element.text, 'child2child1')

        self.tag.empty()
        self.wait_until(lambda: self.element.text == '')
        self.assertEqual(self.element.text, '')
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c1, self.wait_time * 10)
        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c2, self.wait_time * 10)

    def test_add_df(self):
        self.set_element(self.tag)
        self.df.append(self.c1, self.c2, 'text')
        self.tag.appendChild(self.df)
        self.wait_until(lambda: self.element.text == 'child1child2text')
        self.assertEqual(self.element.text, 'child1child2text')

        df = DocumentFragment()
        df.append(self.c3, 'text2')
        self.tag.appendChild(df)
        self.wait_until(
            lambda: self.element.text == 'child1child2textchild3text2')
        self.assertEqual(self.element.text, 'child1child2textchild3text2')

    def test_insert_df(self):
        self.set_element(self.tag)
        self.tag.appendChild(self.c1)
        self.df.append(self.c2, self.c3, 'text')
        self.tag.insertBefore(self.df, self.c1)
        self.wait_until(lambda: self.element.text == 'child2child3textchild1')
        self.assertEqual(self.element.text, 'child2child3textchild1')

        df = DocumentFragment()
        df.append(self.c4, 'text2')
        self.tag.insertBefore(df, self.c3)
        self.wait_until(
            lambda: self.element.text == 'child2child4text2child3textchild1')
        self.assertEqual(self.element.text,
                         'child2child4text2child3textchild1')

    def test_replace_child(self):
        self.set_element(self.tag)
        self.tag.appendChild(self.c1)

        with self.assertRaises(NoSuchElementException):
            self.set_element(self.c2, self.wait_time * 10)
        self.assertIsTrue(self.set_element(self.c1))
        self.wait_until(lambda: self.element.text == 'child1')
        self.assertEqual(self.element.text, 'child1')

        self.tag.replaceChild(self.c2, self.c1)
        with self.assertRaises(NoSuchElementException):
            self.wait(0.1)
            self.set_element(self.c1, self.wait_time * 10)
        self.assertIsTrue(self.set_element(self.c2))
        self.wait_until(lambda: self.element.text == 'child2')
        self.assertEqual(self.element.text, 'child2')
        self.set_element(self.tag)
        self.wait_until(lambda: self.element.text == 'child2')
        self.assertEqual(self.element.text, 'child2')

    def test_append(self):
        self.set_element(self.tag)
        self.tag.append(self.c1)
        self.wait_until(lambda: self.element.text == 'child1')
        self.assertEqual(self.element.text, 'child1')

        self.tag.append(self.c2, self.c3)
        self.wait_until(lambda: self.element.text == 'child1child2child3')
        self.assertEqual(self.element.text, 'child1child2child3')

        self.tag.append(self.c4, self.c1)
        self.wait_until(
            lambda: self.element.text == 'child2child3child4child1')
        self.assertEqual(self.element.text, 'child2child3child4child1')

        self.tag.append('t1', 't2')
        self.wait_until(
            lambda: self.element.text == 'child2child3child4child1t1t2')
        self.assertEqual(self.element.text, 'child2child3child4child1t1t2')

    def test_prepend(self):
        self.set_element(self.tag)
        self.tag.prepend(self.c1)
        self.wait_until(lambda: self.element.text == 'child1')
        self.assertEqual(self.element.text, 'child1')

        self.tag.prepend(self.c2, self.c3)
        self.wait_until(lambda: self.element.text == 'child2child3child1')
        self.assertEqual(self.element.text, 'child2child3child1')

        self.tag.prepend(self.c4, self.c1)
        self.wait_until(
            lambda: self.element.text == 'child4child1child2child3')
        self.assertEqual(self.element.text, 'child4child1child2child3')

        self.tag.prepend('t1', 't2')
        self.wait_until(
            lambda: self.element.text == 't1t2child4child1child2child3')
        self.assertEqual(self.element.text, 't1t2child4child1child2child3')

    def test_prepend_append_text(self):
        self.set_element(self.tag)
        self.tag.append('t1')
        self.wait_until(lambda: self.element.text == 't1')
        self.assertEqual(self.element.text, 't1')

        self.tag.firstChild.remove()
        self.wait_until(lambda: self.element.text == '')
        self.assertEqual(self.element.text, '')

        self.tag.prepend('t2')
        self.wait_until(lambda: self.element.text == 't2')
        self.assertEqual(self.element.text, 't2')

        self.tag.append('t3', 't4')
        self.wait_until(lambda: self.element.text == 't2t3t4')
        self.assertEqual(self.element.text, 't2t3t4')

        self.tag.prepend('t5', 't6')
        self.wait_until(lambda: self.element.text == 't5t6t2t3t4')
        self.assertEqual(self.element.text, 't5t6t2t3t4')

    def test_after(self):
        self.set_element(self.tag)
        self.tag.append(self.c1)
        self.c1.after(self.c2)
        self.wait_until(lambda: self.element.text == 'child1child2')
        self.assertEqual(self.element.text, 'child1child2')

        self.c1.after(self.c3, self.c4)
        self.wait_until(
            lambda: self.element.text == 'child1child3child4child2')
        self.assertEqual(self.element.text, 'child1child3child4child2')

        self.c1.after(self.c2, 'text')
        self.wait_until(
            lambda: self.element.text == 'child1child2textchild3child4')
        self.assertEqual(self.element.text, 'child1child2textchild3child4')

    def test_before(self):
        self.set_element(self.tag)
        self.tag.append(self.c1)
        self.c1.before(self.c2)
        self.wait_until(lambda: self.element.text == 'child2child1')
        self.assertEqual(self.element.text, 'child2child1')

        self.c1.before(self.c3, self.c4)
        self.wait_until(
            lambda: self.element.text == 'child2child3child4child1')
        self.assertEqual(self.element.text, 'child2child3child4child1')

        self.c1.before(self.c2, 'text')
        self.wait_until(
            lambda: self.element.text == 'child3child4child2textchild1')
        self.assertEqual(self.element.text, 'child3child4child2textchild1')

    def test_after_before_text(self):
        self.set_element(self.tag)
        self.tag.append('a')
        t = self.tag.firstChild
        t.after('b')
        self.wait_until(lambda: self.element.text == 'ab')
        self.assertEqual(self.element.text, 'ab')

        t.after('c', 'd')
        self.wait_until(lambda: self.element.text == 'acdb')
        self.assertEqual(self.element.text, 'acdb')

        t.before('e')
        self.wait_until(lambda: self.element.text == 'eacdb')
        self.assertEqual(self.element.text, 'eacdb')

        t.before('f', 'g')
        self.wait_until(lambda: self.element.text == 'efgacdb')
        self.assertEqual(self.element.text, 'efgacdb')

    def test_shortcut_attr(self):
        self.tag.textContent = 'TAG'
        self.set_element(self.tag)
        self.wait_until(lambda: self.element.is_displayed())
        self.assertIsTrue(self.element.is_displayed())
        self.tag.hidden = True
        self.wait_until(lambda: not self.element.is_displayed())
        self.assertIsFalse(self.element.is_displayed())
        self.tag.hidden = False
        self.wait_until(lambda: self.element.is_displayed())
        self.assertIsTrue(self.element.is_displayed())

    def test_style(self):
        self.tag.textContent = 'Style'
        self.set_element(self.tag)
        self.wait_until(lambda: self.element.get_attribute('style') == '')
        self.assertEqual(self.element.get_attribute('style'), '')
        style = 'color: red;'
        self.tag.style = style
        self.wait_until(lambda: self.element.get_attribute('style') == style)
        self.assertEqual(self.element.get_attribute('style'), style)
        self.tag.style.color = 'black'
        self.wait_until(
            lambda: self.element.get_attribute('style') == 'color: black;')
        self.assertEqual(self.element.get_attribute('style'), 'color: black;')

    def test_classlist(self):
        self.set_element(self.tag)
        self.assertEqual(self.element.get_attribute('class'), '')
        self.tag.classList.add('a')
        self.wait_until(lambda: self.element.get_attribute('class') == 'a')
        self.assertEqual(self.element.get_attribute('class'), 'a')
        self.tag.classList.add('b', 'c', 'd')
        self.wait_until(
            lambda: self.element.get_attribute('class') == 'a b c d')
        self.assertEqual(self.element.get_attribute('class'), 'a b c d')

        self.tag.classList.remove('c')
        self.wait_until(lambda: self.element.get_attribute('class') == 'a b d')
        self.assertEqual(self.element.get_attribute('class'), 'a b d')
        self.tag.classList.remove('a', 'd')
        self.wait_until(lambda: self.element.get_attribute('class') == 'b')
        self.assertEqual(self.element.get_attribute('class'), 'b')

        self.tag.classList.toggle('b')
        self.wait_until(lambda: self.element.get_attribute('class') == '')
        self.assertEqual(self.element.get_attribute('class'), '')
        self.tag.classList.toggle('b')
        self.wait_until(lambda: self.element.get_attribute('class') == 'b')
        self.assertEqual(self.element.get_attribute('class'), 'b')

    def test_click(self):
        mock = MagicMock(_is_coroutine=False)
        self.tag.addEventListener('click', mock)
        self.tag.click()
        self.wait_until(lambda: mock.call_count == 1)
        self.assertEqual(mock.call_count, 1)

    @sync
    @asyncio.coroutine
    def test_get_rect(self):
        rect = WebElement('div', style='width:200px;height:100px;')
        self.tag.appendChild(rect)
        yield from asyncio.sleep(self.wait_time)

        data = yield from rect.getBoundingClientRect()
        self.assertEqual(data['width'], 200)
        self.assertEqual(data['height'], 100)

    @sync
    @asyncio.coroutine
    def test_scroll(self):
        rect = WebElement('div',
                          style='width:3000px;height:3000px;background:#eee;')
        self.tag.appendChild(rect)
        yield from asyncio.sleep(self.wait_time)

        X = yield from rect.scrollX()
        Y = yield from rect.scrollY()
        self.assertEqual(X['x'], 0)
        self.assertEqual(Y['y'], 0)

        rect.scrollTo(200, 200)
        yield from asyncio.sleep(self.wait_time)
        X = yield from rect.scrollX()
        Y = yield from rect.scrollY()
        self.assertEqual(X['x'], 200)
        self.assertEqual(Y['y'], 200)

    def test_exec(self):
        self.tag.exec('this.style = "color: red;"')
        self.set_element(self.tag)
        self.wait_until(
            lambda: re.search(r'255,\s*0,\s* 0,\s*1\s*',
                self.element.value_of_css_property('color')))
        self.assertRegex(self.element.value_of_css_property('color'),
                         r'255,\s*0,\s* 0,\s*1\s*')

        self.tag.exec('node.style = "color: blue;"')
        self.wait_until(
            lambda: re.search(r'0,\s*0,\s* 255,\s*1\s*',
                self.element.value_of_css_property('color')))
        self.assertRegex(self.element.value_of_css_property('color'),
                         r'0,\s*0,\s*255,\s*1\s*')

    def test_exec_error(self):
        with self.assertLogs('wdom.server', 'ERROR') as log:
            self.tag.exec('a.b')
            self.wait_until(lambda: len(log.output) > 0)
        self.assertRegex(log.output[0], r'JS: ReferenceError')


class TestEvent(ElementTestCase, TestCase):
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
        # need to wait some times
        self.wait(times=10)
        self.set_element(self.btn)
        self.wait(times=10)
        self.element.click()
        self.wait(times=10)
        self.wait_until(lambda: self.click_event_mock.call_count == 1)
        self.assertEqual(self.click_event_mock.call_count, 1)

    def test_input(self):
        self.set_element(self.input)
        self.element.send_keys('abc')
        self.wait_until(lambda: self.input_event_mock.call_count == 3)
        self.assertEqual(self.input_event_mock.call_count, 3)
