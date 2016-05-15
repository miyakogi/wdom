#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

from selenium.webdriver.common.keys import Keys

from wdom.tag import H1
from wdom.document import get_document
from wdom.misc import install_asyncio
from wdom.testing import WebDriverTestCase, TestCase, reset
from wdom.testing import close_webdriver


def setUpModule():
    install_asyncio()


def tearDownModule():
    close_webdriver()


class SimpleTestCase(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        reset()  # I don't know why, but need reset for aiohttp.
        self.document = get_document()
        self.h1 = H1()
        self.h1.textContent = 'TITLE'
        self.document.body.appendChild(self.h1)
        self.start()

    def test_page(self):
        tag = self.wd.find_element_by_css_selector(
            '[rimo_id="{}"]'.format(self.h1.rimo_id))
        self.assertEqual(tag.text, 'TITLE')


class TestDataBinding(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        reset()  # I don't know why, but need reset for aiohttp.
        from wdom.examples.data_binding import sample_page
        self.document = sample_page(autoreload=False)
        self.start()

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_app(self):
        view = self.wd.find_element_by_tag_name('h1')
        self.assertEqual(view.text, 'Hello!')
        input = self.wd.find_element_by_tag_name('input')
        self.send_keys(input, 'abcde')
        self.wait_until(lambda: view.text == 'abcde')
        self.assertEqual(view.text, 'abcde')
        for i in range(5):
            self.send_keys(input, Keys.BACKSPACE)
        self.wait_until(lambda: view.text == '')
        self.assertEqual(view.text, '')
        self.send_keys(input, 'new')
        self.wait_until(lambda: view.text == 'new')
        self.assertEqual(view.text, 'new')


class TestRevText(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        reset()  # I don't know why, but need reset for aiohttp.
        from wdom.examples.rev_text import sample_page
        self.document = sample_page(autoreload=False)
        self.start()

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_app(self):
        view = self.wd.find_element_by_tag_name('h1')
        text = 'Click!'
        self.assertEqual(view.text, text)
        # need long wait time
        self.wait(times=20)
        view.click()
        self.wait(times=20)
        self.wait_until(lambda: view.text == text[::-1])
        self.assertEqual(view.text, text[::-1])
        self.wait(times=20)
        view.click()
        self.wait(times=20)
        self.wait_until(lambda: view.text == text)
        self.assertEqual(view.text, text)


class TestTimer(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        reset()  # I don't know why, but need reset for aiohttp.
        from wdom.examples.timer import sample_page
        self.document = sample_page(autoreload=False)
        self.start()

    @unittest.skipIf(os.environ.get('TRAVIS', False),
                     reason='This test not pass only on travis')
    def test_timer(self):
        view = self.wd.find_element_by_tag_name('h1')
        start_btn = self.wd.find_element_by_id('start_btn')
        stop_btn = self.wd.find_element_by_id('stop_btn')
        reset_btn = self.wd.find_element_by_id('reset_btn')
        self.wait(times=20)

        def test_timer():
            self.assertEqual(view.text, '180.00')
            start_btn.click()
            self.wait(times=20)
            self.assertTrue(float(view.text) < 179.90)
            stop_btn.click()
            t = view.text
            self.wait(times=20)
            self.assertEqual(view.text, t)

        test_timer()
        reset_btn.click()
        self.wait(times=20)
        test_timer()
