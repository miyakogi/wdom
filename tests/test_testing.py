#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from wdom import testing
from wdom.document import get_document


class TestInitialize(unittest.TestCase):
    def test_initialize(self):
        from wdom.server import _tornado
        old_doc = get_document()
        old_app_tornado = _tornado.get_app()
        testing.reset()
        self.assertIsNot(old_doc, get_document())
        self.assertIsNot(old_app_tornado, _tornado.get_app())
        try:
            from wdom.server import _aiohttp
            old_app_aio = _aiohttp.get_app()
            testing.reset()
            self.assertIsNot(old_app_aio, _aiohttp.get_app())
        except ImportError:
            pass
