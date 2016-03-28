#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from wdom.tag import H1
from wdom.document import get_document
from wdom import server_aio
from wdom.misc import install_asyncio
from wdom.tests.ui import wd

from wdom.examples.data_binding import sample_page


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
        self.document = sample_page(autoreload=False)
        h1 = H1()
        h1.textContent = 'TITLE'
        self.document.body.append(h1)
        self.app = self.module.get_app(self.document)
        return self.app

    def test_app(self):
        self.wd.get(self.url)
        assert True


class TestSimplePage(SimpleTestCase, unittest.TestCase):
    module = server_aio

class TestDataBinding(DataBindingTestCase, unittest.TestCase):
    module = server_aio
