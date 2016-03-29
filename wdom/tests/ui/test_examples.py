#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from selenium.webdriver.common.keys import Keys

from wdom.tag import H1
from wdom.document import get_document
from wdom import server_aio
from wdom.misc import install_asyncio
from wdom.tests.ui import wd


def setUpModule():
    install_asyncio()
    wd.start_wd()


def tearDownModule():
    wd.close_wd()


class SimpleTestCase(wd.UITest):
    def get_app(self):
        self.document = get_document(autoreload=False)
        self.h1 = H1()
        self.h1.textContent = 'TITLE'
        self.document.body.appendChild(self.h1)
        self.app = self.module.get_app(self.document)
        return self.app

    def test_page(self):
        tag = self.wd.find_element_by_id(self.h1.id)
        assert tag.text == 'TITLE'


class DataBindingTestCase(wd.UITest):
    def get_app(self):
        from wdom.examples.data_binding import sample_page
        self.document = sample_page(autoreload=False)
        self.app = self.module.get_app(self.document)
        return self.app

    def test_app(self):
        view = self.wd.find_element_by_tag_name('h1')
        self.assertEqual(view.text, 'Hello!')
        input = self.wd.find_element_by_tag_name('input')
        self.send_keys(input, 'abcde')
        self.wait()
        self.assertEqual(view.text, 'abcde')
        for i in range(5):
            self.send_keys(input, Keys.BACKSPACE)
        self.wait()
        self.assertEqual(view.text, '')
        self.send_keys(input, 'new')
        self.wait()
        self.assertEqual(view.text, 'new')


class RevTextTestCase(wd.UITest):
    def get_app(self):
        from wdom.examples.rev_text import sample_page
        self.document = sample_page(autoreload=False)
        self.app = self.module.get_app(self.document)
        return self.app

    def test_app(self):
        view = self.wd.find_element_by_tag_name('h1')
        text = 'Click!'
        self.assertEqual(view.text, text)
        view.click()
        self.wait()
        self.assertEqual(view.text, text[::-1])
        view.click()
        self.wait()
        self.assertEqual(view.text, text)


class TestSimplePage(SimpleTestCase, unittest.TestCase):
    module = server_aio
    wait_time = 0.02


class TestDataBinding(DataBindingTestCase, unittest.TestCase):
    module = server_aio
    wait_time = 0.02


class TestRevText(RevTextTestCase, unittest.TestCase):
    module = server_aio
    wait_time = 0.02
