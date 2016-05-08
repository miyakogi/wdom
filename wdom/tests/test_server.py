#!/usr/bin/env py.test
# -*- coding: utf-8 -*-

import sys
import os
from os import path
import time
import subprocess
import asyncio
import tempfile

from syncer import sync

from selenium.webdriver.common.utils import free_port
from tornado import websocket
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future

from wdom.testing import TestCase

curdir = path.dirname(__file__)
root = path.dirname(path.dirname(curdir))
script = '''
import asyncio
from wdom import misc, document, {module}
misc.install_asyncio()
doc = document.get_document()
with open(doc.tempdir + '/a.html', 'w') as f:
    f.write(doc.tempdir)
{module}.start_server({module}.get_app(doc))
asyncio.get_event_loop().run_forever()
'''


def setUpModule():
    if not IOLoop.initialized():
        AsyncIOMainLoop().install()


class TestServerBase(TestCase):
    module = 'server'
    cmd = []

    def setUp(self):
        super().setUp()
        self.port = free_port()
        env = os.environ.copy()
        env['PYTHONPATH'] = root
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
            self.tmp = f.name
            f.write(script.format(module=self.module))
        cmd = [sys.executable, self.tmp, '--port', str(self.port)] + self.cmd
        self.addr = 'localhost:{}'.format(self.port)
        self.proc = subprocess.Popen(
            cmd, cwd=curdir, env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        time.sleep(0.1)

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)
        if self.proc.returncode is None:
            self.proc.terminate()
        super().tearDown()


class TestAutoShutdownAIO(TestServerBase):
    module = 'server_aio'
    cmd = ['--auto-shutdown', '--shutdown-wait', '0.2']

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

    @sync
    async def test_tempdir_cleanup(self):
        import aiohttp
        await asyncio.sleep(0.1)
        ws = await self.ws_connect('ws://'+self.addr+'/rimo_ws')
        with aiohttp.ClientSession() as session:
            async with session.get('http://'+self.addr+'/tmp/a.html') as response:
                assert response.status == 200
                content = (await response.read()).decode('utf-8')
        self.assertTrue(path.exists(content.strip()))
        self.assertTrue(path.isdir(content.strip()))
        ws.close()
        await asyncio.sleep(0.3)
        self.assertIsNotNone(self.proc.poll())
        self.assertFalse(path.exists(content.strip()))
        self.assertFalse(path.isdir(content.strip()))


class TestOpenBrowser(TestServerBase):
    module = 'server_aio'
    cmd = ['--debug', '--logging', 'info', '--open-browser', '--browser', 'firefox']

    def test_open_browser(self):
        time.sleep(0.5)
        self.assertIn('Start server on', self.proc.stdout.readline())
        self.assertIn('connected', self.proc.stdout.readline())


class TestAutoShutdownTornado(TestAutoShutdownAIO):
    module = 'server_tornado'


class TestOpenBrowserTornado(TestOpenBrowser):
    module = 'server_tornado'
