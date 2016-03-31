#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os.path import dirname
import time
import logging
import asyncio
import subprocess

import aiohttp
from selenium.webdriver.common.utils import free_port
from syncer import sync
from tornado import websocket
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future

from wdom.log import configure_logger
from wdom.tests.util import TestCase
from wdom.document import Document
from wdom.server_aio import get_app, start_server, stop_server


def setUpModule():
    configure_logger(logging.DEBUG)
    if not IOLoop.initialized():
        AsyncIOMainLoop().install()


class TestServer(TestCase):
    def setUp(self):
        with self.assertLogs('wdom.server_aio', 'INFO'):
            self.server = start_server(self.get_app(), port=0)
        self.port = self.server.sockets[-1].getsockname()[1]
        self.addr = 'http://localhost:{}'.format(self.port)

    def get_app(self):
        self.doc = Document()
        self.app = get_app(self.doc)
        return self.app

    def tearDown(self):
        with self.assertLogs('wdom.server_aio', 'INFO'):
            stop_server(self.server)

    async def fetch(self, url:str):
        if not url.startswith('/'):
            url = '/' + url
        loop = asyncio.get_event_loop()
        with aiohttp.ClientSession(loop=loop) as session:
            with self.assertLogs('wdom.server_aio', 'INFO'):
                async with session.get(self.addr + url) as response:
                    assert response.status == 200
                    content = await response.read()
        return content.decode('utf-8')

    @sync
    async def test_mainpage(self):
        content = await self.fetch('/')
        self.assertMatch(
            r'<!DOCTYPE html><html id="\d+">\s*<head id="\d+">\s*'
            r'.*<meta .*<title id="\d+">\s*W-DOM\s*</title>.*'
            r'</head>\s*<body.*>.*<script.*>.*</script>.*'
            r'</body>\s*</html>'
            r'', content
        )


class TestAutoShutdown(TestCase):
    def setUp(self):
        self.root = dirname(dirname(dirname(__file__)))
        self.port = free_port()
        cmd = [sys.executable, '-m', 'wdom', '--port', str(self.port),
               '--autoshutdown', '--shutdown-wait', '0.2']
        self.addr = 'localhost:{}'.format(self.port)
        self.proc = subprocess.Popen(
            cmd, cwd=self.root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.1)

    def tearDown(self):
        self.proc.terminate()

    async def ws_connect(self, url:str):
        for i in range(10):
            await asyncio.sleep(0.05)
            try:
                ws = await to_asyncio_future(websocket.websocket_connect(url))
                return ws
            except Exception:
                continue
            else:
                break
        raise OSError('connection refused')

    @sync
    async def test_autoshutdown(self):
        await asyncio.sleep(0.1)
        ws = await self.ws_connect('ws://'+self.addr+'/rimo_ws')
        ws.close()
        await asyncio.sleep(0.3)
        self.assertIsNotNone(self.proc.poll())

    @sync
    async def test_reload(self):
        await asyncio.sleep(0.1)
        ws = await self.ws_connect('ws://'+self.addr+'/rimo_ws')
        ws.close()
        ws = await self.ws_connect('ws://'+self.addr+'/rimo_ws')
        await asyncio.sleep(0.3)
        self.assertIsNone(self.proc.poll())

    @sync
    async def test_multi_connection(self):
        await asyncio.sleep(0.1)
        ws1 = await self.ws_connect('ws://'+self.addr+'/rimo_ws')
        ws2 = await self.ws_connect('ws://'+self.addr+'/rimo_ws')
        ws1.close()
        await asyncio.sleep(0.3)
        self.assertIsNone(self.proc.poll())
        ws2.close()
        await asyncio.sleep(0.3)
        self.assertIsNotNone(self.proc.poll())
