#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import time
import subprocess
import logging
import asyncio

from syncer import sync

from selenium.webdriver.common.utils import free_port
from tornado import websocket
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future

from wdom.log import configure_logger
from wdom.testing import TestCase


curdir = path.dirname(__file__)


def setUpModule():
    configure_logger(logging.DEBUG)
    if not IOLoop.initialized():
        AsyncIOMainLoop().install()


class TestAutoShutdownAIO(TestCase):
    test_file = path.join(curdir, 'aio_server.py')

    def setUp(self):
        self.port = free_port()
        cmd = [sys.executable, self.test_file, '--port', str(self.port),
               '--auto-shutdown', '--shutdown-wait', '0.2']
        self.addr = 'localhost:{}'.format(self.port)
        self.proc = subprocess.Popen(
            cmd, cwd=curdir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.1)

    def tearDown(self):
        self.proc.terminate()

    async def ws_connect(self, url:str):
        for i in range(20):
            await asyncio.sleep(0.05)
            try:
                ws = await to_asyncio_future(websocket.websocket_connect(url))
                return ws
            except Exception:
                continue
            else:
                break
        raise OSError('connection refused to {}'.format(url))

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


class TestOpenBrowser(TestCase):
    test_file = path.join(curdir, 'aio_server.py')

    def setUp(self):
        self.port = free_port()
        cmd = [sys.executable, self.test_file, '--port', str(self.port),
               '--debug', '--logging', 'info',
               '--open-browser', '--browser', 'firefox']
        self.addr = 'localhost:{}'.format(self.port)
        self.proc = subprocess.Popen(
            cmd, cwd=curdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        time.sleep(0.1)

    def tearDown(self):
        if self.proc.returncode is None:
            self.proc.terminate()

    def test_open_browser(self):
        time.sleep(0.5)
        self.assertIn('Start server on', self.proc.stdout.readline())
        self.assertIn('connected', self.proc.stdout.readline())


class TestAutoShutdownTornado(TestAutoShutdownAIO):
    test_file = path.join(curdir, 'tornado_server.py')


class TestOpenBrowserTornado(TestOpenBrowser):
    test_file = path.join(curdir, 'tornado_server.py')
