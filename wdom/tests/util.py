#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''

import time
import re
import functools
import asyncio
from multiprocessing import Process
import unittest

from tornado.web import Application
from tornado.httpserver import HTTPServer


class TestCase(unittest.TestCase):
    def assertIsTrue(self, bl):
        self.assertIs(bl, True)

    def assertIsFalse(self, bl):
        self.assertIs(bl, False)

    def assertMatch(self, pattern, string):
        self.assertIsNotNone(re.match(pattern, string))

    def assertNotMatch(self, pattern, string):
        self.assertIsNone(re.match(pattern, string))
        return self.wait_for()


def sync(co):
    @functools.wraps(co)
    def run(*args, **kwargs):
        fut = asyncio.ensure_future(co(*args, **kwargs))
        asyncio.get_event_loop().run_until_complete(fut)
        return fut.result()
    return run
