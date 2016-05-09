#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from wdom import testing
from wdom.document import get_document
from wdom import server_aio, server_tornado


class TestInitialize(unittest.TestCase):
    def test_initialize(self):
        old_doc = get_document()
        old_app_aio = server_aio.get_app()
        old_app_tornado = server_tornado.get_app()
        testing.initialize()
        self.assertIsNot(old_doc, get_document())
        self.assertIsNot(old_app_aio, server_aio.get_app())
        self.assertIsNot(old_app_tornado, server_tornado.get_app())


class TestInitializeTestCase(testing.TestCase):
    @classmethod
    def setUpClass(self):
        self.old_doc = get_document()
        self.old_app_aio = server_aio.get_app()
        self.old_app_tornado = server_tornado.get_app()

    def test_initialize(self):
        self.assertIsNot(self.old_doc, get_document())
        self.assertIsNot(self.old_app_aio, server_aio.get_app())
        self.assertIsNot(self.old_app_tornado, server_tornado.get_app())
