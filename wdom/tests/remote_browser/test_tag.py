#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

from selenium.common.exceptions import NoSuchElementException

from wdom.tag import Tag, Textarea, Input, CheckBox, Div, Select, Option, Form
from wdom.tag import Label
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.testing import RemoteBrowserTestCase, TestCase
from wdom.testing import start_remote_browser, close_remote_browser


def setUpModule():
    install_asyncio()
    start_remote_browser()


def tearDownModule():
    close_remote_browser()


class TestTag(RemoteBrowserTestCase, TestCase):
    if os.environ.get('TRAVIS', False):
        wait_time = 0.1

    def setUp(self):
        super().setUp()
        self.document = get_document()

        class Root(Tag):
            tag = 'root'
        self.root = Root()
        self.document.body.prepend(self.root)
        self.start()
        self.set_element(self.root)

    def test_connection(self):
        self.assertIsTrue(self.root.connected)
        # this is an example, but valid domain for test
        self.browser.get('http://example.com/')
        self.assertIsFalse(self.root.connected)

    def test_node_text(self):
        self.assertEqual(self.element.text, '')
        self.root.textContent = 'ROOT'
        self.wait_until(lambda: self.element.text == 'ROOT')
        self.assertEqual(self.element.text, 'ROOT')

    def test_node_attr(self):
        self.assertIsNone(self.element.get_attribute('src'))
        self.root.setAttribute('src', 'a')
        self.wait_until(lambda: self.element.get_attribute('src') == 'a')
        self.assertEqual(self.element.get_attribute('src'), 'a')
        self.root.removeAttribute('src')
        self.wait_until(lambda: self.element.get_attribute('src') is None)
        self.assertIsNone(self.element.get_attribute('src'))

    def test_node_class(self):
        self.root.addClass('a')
        self.wait_until(lambda: self.element.get_attribute('class') == 'a')
        self.assertEqual(self.element.get_attribute('class'), 'a')
        self.root.removeClass('a')
        self.wait_until(lambda: self.element.get_attribute('class') == '')
        self.assertEqual(self.element.get_attribute('class'), '')

    def test_addremove_child(self):
        child = Tag()
        self.root.appendChild(child)
        self.set_element(child)
        self.wait_until(lambda: self.element.text == '')
        self.assertEqual(self.element.text, '')
        child.textContent = 'Child'
        self.wait_until(lambda: self.element.text == 'Child')
        self.assertEqual(self.element.text, 'Child')

        self.root.removeChild(child)
        with self.assertRaises(NoSuchElementException):
            self.wait(0.1)
            self.set_element(child, self.wait_time * 10)

    def test_replace_child(self):
        child1 = Tag()
        child1.textContent = 'child1'
        child2 = Tag()
        child2.textContent = 'child2'
        self.root.appendChild(child1)
        with self.assertRaises(NoSuchElementException):
            self.set_element(child2, self.wait_time * 10)
        self.set_element(child1)
        self.wait_until(lambda: self.element.text == 'child1')
        self.assertEqual(self.element.text, 'child1')

        self.root.replaceChild(child2, child1)
        with self.assertRaises(NoSuchElementException):
            self.wait(0.1)
            self.set_element(child1, self.wait_time * 10)
        self.set_element(child2)
        self.wait_until(lambda: self.element.text == 'child2')
        self.assertEqual(self.element.text, 'child2')

    def test_showhide(self):
        self.root.textContent = 'root'
        self.wait_until(lambda: self.element.is_displayed())
        self.assertIsTrue(self.element.is_displayed())
        self.root.hide()
        self.wait_until(lambda: not self.element.is_displayed())
        self.assertIsFalse(self.element.is_displayed())
        self.root.show()
        self.wait_until(lambda: self.element.is_displayed())
        self.assertIsTrue(self.element.is_displayed())


class TestInput(RemoteBrowserTestCase, TestCase):
    if os.environ.get('TRAVIS', False):
        wait_time = 0.1

    def setUp(self):
        super().setUp()
        self.document = get_document(autoreload=False)
        self.root = Form()
        self.input = Input(parent=self.root, type='text')
        self.textarea = Textarea(parent=self.root)
        self.checkbox = CheckBox(parent=self.root, id='check1')
        self.check_l = Label('Check 1', parent=self.root, **{'for': 'check1'})
        self.radio1 = Input(parent=self.root, type='radio', name='radio_test', id='r1')  # noqa
        self.radio2 = Input(parent=self.root, type='radio', name='radio_test', id='r2')  # noqa
        self.radio3 = Input(parent=self.root, type='radio', name='radio_test2', id='r3')  # noqa
        self.radio1_l = Label('Radio 1', parent=self.root, **{'for': 'r1'})
        self.radio2_l = Label('Radio 2', parent=self.root, **{'for': 'r2'})
        self.radio3_l = Label('Radio 3', parent=self.root, **{'for': 'r3'})
        self.document.body.prepend(self.root)
        self.start()

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_textinput(self):
        self.set_element(self.input)
        self.element.send_keys('abc')
        self.wait_until(lambda: self.input.value == 'abc')
        self.assertEqual(self.input.value, 'abc')

        self.browser.get(self.url)
        self.set_element(self.input)
        self.wait_until(lambda: self.element.get_attribute('value') == 'abc')
        self.assertEqual(self.element.get_attribute('value'), 'abc')

        self.element.send_keys('def')
        self.wait_until(
            lambda: self.element.get_attribute('value') == 'abcdef')
        self.assertEqual(self.input.value, 'abcdef')

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_textarea(self):
        self.set_element(self.textarea)
        self.element.send_keys('abc')
        self.wait_until(lambda: self.textarea.value == 'abc')
        self.assertEqual(self.textarea.value, 'abc')

        self.browser.get(self.url)
        self.set_element(self.textarea)
        self.wait_until(lambda: self.element.get_attribute('value') == 'abc')
        self.assertEqual(self.element.get_attribute('value'), 'abc')

        self.element.send_keys('def')
        self.wait_until(
            lambda: self.element.get_attribute('value') == 'abcdef')
        self.assertEqual(self.textarea.value, 'abcdef')

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_checkbox(self):
        self.set_element(self.checkbox)
        self.element.click()
        self.wait_until(lambda: self.checkbox.checked)
        self.assertIsTrue(self.checkbox.checked)

        self.browser.get(self.url)
        self.set_element(self.checkbox)
        self.wait_until(
            lambda: self.element.get_attribute('checked') == 'true')
        self.assertEqual(self.element.get_attribute('checked'), 'true')

        self.element.click()
        self.wait_until(
            lambda: self.element.get_attribute('checked') is None)
        self.assertIsNone(self.element.get_attribute('checked'))
        self.assertIsFalse(self.checkbox.checked)

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_checkbox_label(self):
        self.set_element(self.check_l)
        self.element.click()
        self.wait_until(lambda: self.checkbox.checked)
        self.assertTrue(self.checkbox.checked)

        self.element.click()
        self.wait_until(lambda: not self.checkbox.checked)
        self.assertFalse(self.checkbox.checked)

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_radios(self):
        self.assertFalse(self.radio1.checked)
        self.assertFalse(self.radio2.checked)
        self.assertFalse(self.radio3.checked)

        self.set_element(self.radio1)
        self.element.click()
        self.wait_until(lambda: self.radio1.checked)
        self.assertTrue(self.radio1.checked)
        self.assertFalse(self.radio2.checked)
        self.assertFalse(self.radio3.checked)

        self.set_element(self.radio2)
        self.element.click()
        self.wait_until(lambda: self.radio2.checked)
        self.assertFalse(self.radio1.checked)
        self.assertTrue(self.radio2.checked)
        self.assertFalse(self.radio3.checked)

        self.set_element(self.radio3)
        self.element.click()
        self.wait_until(lambda: self.radio3.checked)
        self.assertFalse(self.radio1.checked)
        self.assertTrue(self.radio2.checked)
        self.assertTrue(self.radio3.checked)

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_radios_label(self):
        self.set_element(self.radio1_l)
        self.element.click()
        self.wait_until(lambda: self.radio1.checked)
        self.assertTrue(self.radio1.checked)
        self.assertFalse(self.radio2.checked)

        self.set_element(self.radio2_l)
        self.element.click()
        self.wait_until(lambda: self.radio2.checked)
        self.assertFalse(self.radio1.checked)
        self.assertTrue(self.radio2.checked)


class TestSelect(RemoteBrowserTestCase, TestCase):
    if os.environ.get('TRAVIS', False):
        wait_time = 0.1

    def setUp(self):
        super().setUp()
        self.document = get_document(autoreload=False)
        self.root = Div()
        self.select = Select(parent=self.root)
        self.mselect = Select(parent=self.root, multiple=True)
        self.opt1 = Option('option 1', parent=self.select)
        self.opt2 = Option('option 2', parent=self.select)
        self.opt3 = Option('option 3', parent=self.select, value='opt3')
        self.opt1m = Option('option 1', parent=self.mselect)
        self.opt2m = Option('option 2', parent=self.mselect)
        self.opt3m = Option('option 3', parent=self.mselect, value='opt3m')
        self.document.body.prepend(self.root)
        self.start()

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_select(self):
        self.set_element(self.select)
        self.element.select_by_index(1)
        self.wait_until(lambda: self.opt2.selected)
        self.assertEqual(self.select.value, 'option 2')
        self.assertFalse(self.opt1.selected)
        self.assertTrue(self.opt2.selected)
        self.assertFalse(self.opt3.selected)

        self.element.select_by_visible_text('option 1')
        self.wait_until(lambda: self.opt1.selected)
        self.assertEqual(self.select.value, 'option 1')
        self.assertTrue(self.opt1.selected)
        self.assertFalse(self.opt2.selected)
        self.assertFalse(self.opt3.selected)

        self.element.select_by_value('opt3')
        self.wait_until(lambda: self.opt3.selected)
        self.assertEqual(self.select.value, 'opt3')
        self.assertFalse(self.opt1.selected)
        self.assertFalse(self.opt2.selected)
        self.assertTrue(self.opt3.selected)

    def test_multi_select(self):
        self.set_element(self.mselect)
        self.element.select_by_index(1)
        self.wait_until(lambda: self.opt2m.selected)
        self.assertEqual(self.mselect.value, 'option 2')
        self.assertFalse(self.opt1m.selected)
        self.assertTrue(self.opt2m.selected)
        self.assertFalse(self.opt3m.selected)

        self.element.select_by_index(2)
        self.wait_until(lambda: self.opt3m.selected)
        self.assertFalse(self.opt1m.selected)
        self.assertTrue(self.opt2m.selected)
        self.assertTrue(self.opt3m.selected)

        self.element.deselect_all()
        self.wait_until(lambda: not self.opt3m.selected)
        self.assertFalse(self.opt1m.selected)
        self.assertFalse(self.opt2m.selected)
        self.assertFalse(self.opt3m.selected)
