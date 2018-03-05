#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os

from pyppeteer.launcher import launch
from syncer import sync

from wdom.document import get_document
from wdom import server

from ..base import TestCase

server_config = server.server_config


class PyppeteerTestCase(TestCase):
    if os.getenv('TRAVIS', False):
        wait_time = 0.1
    else:
        wait_time = 0.05

    @classmethod
    def setUpClass(cls):
        cls.browser = launch(args=['--no-sandbox'])
        cls.page = sync(cls.browser.newPage())

    @classmethod
    def tearDownClass(cls):
        sync(cls.browser.close())

    def setUp(self):
        from syncer import sync
        super().setUp()
        self.doc = get_document()
        self.root = self.get_elements()
        self.doc.body.prepend(self.root)
        self.server = server.start_server(port=0)
        self.address = server_config['address']
        self.port = server_config['port']
        self.url = 'http://{}:{}'.format(self.address, self.port)
        sync(self.page.goto(self.url))
        self.element = sync(self.get_element_handle(self.root))

    def tearDown(self):
        server.stop_server(self.server)
        super().tearDown()
        import time
        time.sleep(0.01)

    def get_elements(self):
        raise NotImplementedError

    async def get_element_handle(self, elm):
        result = await self.page.querySelector(
            '[wdom_id="{}"]'.format(elm.wdom_id))
        return result

    async def get_text(self, elm=None):
        elm = elm or self.element
        result = await self.page.evaluate('(elm) => elm.textContent', elm)
        return result

    async def get_attribute(self, name, elm=None):
        elm = elm or self.element
        result = await self.page.evaluate(
            '(elm) => elm.getAttribute("{}")'.format(name), elm)
        return result

    async def wait(self, timeout=None):
        timeout = timeout or self.wait_time
        _t = timeout / 10
        for _ in range(10):
            await asyncio.sleep(_t)

    async def wait_for_element(self, elm):
        await self.page.waitForSelector(
            '[wdom_id="{}"]'.format(elm.wdom_id),
            {'timeout': 100},
        )
