#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from os import path
import re
import json
import time
import subprocess
import unittest

from selenium.webdriver.common.utils import free_port
from syncer import sync

from wdom import server
from wdom.document import get_document
from wdom.util import suppress_logging

from .base import HTTPTestCase

curdir = path.dirname(__file__)
root = path.dirname(path.dirname(curdir))
script = '''
from wdom import document, server
doc = document.get_document()
with open(doc.tempdir + '/a.html', 'w') as f:
    f.write(doc.tempdir)
server.start()
'''


def setUpModule():
    suppress_logging()


class TestServerBase(HTTPTestCase):
    cmd = []

    def setUp(self):
        super().setUp()
        self.port = free_port()
        sync(self.wait(times=3))
        cmd = [
            sys.executable, '-c', script,
            '--port', str(self.port)
        ] + self.cmd
        self.url = 'http://localhost:{}'.format(self.port)
        self.ws_url = 'ws://localhost:{}/wdom_ws'.format(self.port)
        self.proc = subprocess.Popen(
            cmd, cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=0,
        )
        sync(self.wait(times=10))

    def tearDown(self):
        if self.proc.returncode is None:
            self.proc.terminate()
        self.proc.wait()
        self.proc.poll()
        sync(self.wait(times=10))
        super().tearDown()


class TestAutoShutdown(TestServerBase):
    cmd = ['--auto-shutdown', '--shutdown-wait', '0.1']

    @sync
    async def test_autoshutdown(self):
        await self.wait()
        ws = await self.ws_connect(self.ws_url)
        ws.close()
        await self.wait(timeout=0.1, times=5)
        self.assertIsNotNone(self.proc.poll())

    @sync
    async def test_reload(self):
        await self.wait()
        ws = await self.ws_connect(self.ws_url)
        ws.close()
        ws = await self.ws_connect(self.ws_url)
        await self.wait(timeout=0.1, times=5)
        self.assertIsNone(self.proc.poll())
        ws.close()

    @sync
    async def test_multi_connection(self):
        await self.wait()
        ws1 = await self.ws_connect(self.ws_url)
        ws2 = await self.ws_connect(self.ws_url)
        ws1.close()
        await self.wait(timeout=0.1, times=5)
        self.assertIsNone(self.proc.poll())
        ws2.close()
        await self.wait(timeout=0.1, times=5)
        self.assertIsNotNone(self.proc.poll())

    @sync
    async def test_tempdir_cleanup(self):
        await self.wait()
        ws = await self.ws_connect(self.ws_url)
        resp = await self.fetch(self.url + '/tmp/a.html')
        content = resp.body
        self.assertTrue(path.exists(content.strip()))
        self.assertTrue(path.isdir(content.strip()))
        ws.close()
        await self.wait(timeout=0.1, times=5)
        self.assertIsNotNone(self.proc.poll())
        self.assertFalse(path.exists(content.strip()))
        self.assertFalse(path.isdir(content.strip()))


class TestOpenBrowser(TestServerBase):
    cmd = ['--debug', '--open-browser']

    @unittest.skipIf(os.getenv('TOX', False), 'Not test browser on TOX')
    @unittest.skipIf(os.getenv('TRAVIS', False), 'Not test browser on TRAVIS')
    def test_open_browser(self):
        time.sleep(3)
        # terminate server and gett all log
        self.proc.terminate()
        log = self.proc.stdout.read()
        self.assertIn('Start server on', log)
        self.assertIn('connected', log)


class TestOpenBrowserFreePort(TestServerBase):
    cmd = ['--port', '0', '--open-browser']

    @unittest.skipIf(os.getenv('TOX', False), 'Not test browser on TOX')
    @unittest.skipIf(os.getenv('TRAVIS', False), 'Not test browser on TRAVIS')
    def test_open_browser_free_port(self):
        time.sleep(3)
        # terminate server and gett all log
        self.proc.terminate()
        log = self.proc.stdout.read()
        self.assertIn('Start server on', log)
        self.assertIn('connected', log)


class TestMainHandlerBlank(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = get_document()
        self.start()

    @sync
    async def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom', 'INFO'):
            res = await self.fetch(self.url)
        self.assertEqual(res.code, 200)
        _re = re.compile(
            '<!DOCTYPE html>\s*<html wdom_id="\d+">\s*<head wdom_id="\d+">'
            '.*<meta .*<title wdom_id="\d+">\s*W-DOM\s*</title>.*'
            '</head>\s*<body.*>.*<script.*>.*</script>.*'
            '</body>\s*</html>',
            re.S)
        self.assertIsNotNone(_re.match(res.text))


class TestMainHandler(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = get_document()
        self.document.body.prepend('testing')
        self.start()

    @sync
    async def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom', 'INFO'):
            res = await self.fetch(self.url)
        self.assertEqual(res.code, 200)
        self.assertIn('testing', res.text)


class TestStaticFileHandler(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = get_document()
        self.start()

    @sync
    async def test_static_file(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            res = await self.fetch(self.url + '/_static/js/wdom.js')
        self.assertEqual(res.code, 200)
        self.assertIn('wdom', res.text)
        self.assertIn('wdom.log', res.text)

    @sync
    async def test_tempdir(self):
        self.assertTrue(path.exists(self.document.tempdir))
        with self.assertLogs('wdom.server', 'INFO'):
            res = await self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(res.code, 404)
        self.assertIn('404', res.text)
        self.assertIn('Not Found', res.text)
        tmp = path.join(self.document.tempdir, 'a.html')
        with open(tmp, 'w') as f:
            f.write('test')
        self.assertTrue(path.exists(tmp))
        with self.assertLogs('wdom.server', 'INFO'):
            res = await self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(res.code, 200)
        self.assertEqual('test', res.text)

    @sync
    async def test_tempfile(self):
        doc = get_document()
        self.assertTrue(path.exists(doc.tempdir))
        tmp = path.join(doc.tempdir, 'a.html')
        self.assertFalse(path.exists(tmp))
        with open(tmp, 'w') as f:
            f.write('test')
        self.assertTrue(path.exists(tmp))
        response = await self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.text, 'test')

    @sync
    async def test_tempfile_404(self):
        response = await self.fetch(self.url + '/tmp/b.html')
        self.assertEqual(response.code, 404)
        response = await self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(response.code, 404)


class TestAddStaticPath(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        server.add_static_path('a', path.abspath(path.dirname(__file__)))
        self.document = get_document()
        self.start()

    @sync
    async def test_add_static_path(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            res = await self.fetch(self.url + '/a/' + __file__)
        self.assertEqual(res.code, 200)
        self.assertIn('this text', res.text)


class TestRootWSHandler(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.start()
        sync(self.wait())
        self.ws_url = 'ws://localhost:{}/wdom_ws'.format(self.port)
        self.ws = sync(self.ws_connect(self.ws_url))

    @sync
    async def test_ws_connection(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            _ = await self.ws_connect(self.ws_url)
            del _
            await self.wait()

    @sync
    async def test_logging_error(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                [dict(type='log', level='error', message='test')]
            ))
            await self.wait()

    @sync
    async def test_logging_warn(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                [dict(type='log', level='warn', message='test')]
            ))
            await self.wait()

    @sync
    async def test_logging_info(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                [dict(type='log', level='info', message='test')]
            ))
            await self.wait()

    @sync
    async def test_logging_debug(self) -> None:
        with self.assertLogs('wdom.server', 'DEBUG'):
            self.ws.write_message(json.dumps(
                [dict(type='log', level='debug', message='test')]
            ))
            await self.wait()
