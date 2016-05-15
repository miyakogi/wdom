#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from os import path
import re
import json
import time
import subprocess
import asyncio
import tempfile

from selenium.webdriver.common.utils import free_port
from syncer import sync

from wdom.misc import install_asyncio
from wdom.document import get_document
from wdom import server
from wdom.testing import TestCase, HTTPTestCase

curdir = path.dirname(__file__)
root = path.dirname(path.dirname(curdir))
script = '''
import asyncio
import atexit
from wdom import document, server
doc = document.get_document()
with open(doc.tempdir + '/a.html', 'w') as f:
    f.write(doc.tempdir)
server.start_server()
atexit.register(server.stop_server)
try:
    asyncio.get_event_loop().run_forever()
except:
    server.stop_server()
'''


def setUpModule():
    install_asyncio()


class TestServerTypeSet(TestCase):
    def test_server_module(self):
        from wdom.server import _tornado
        server.set_server_type('tornado')
        self.assertTrue(isinstance(server.get_app(), _tornado.Application))
        try:
            from wdom.server import _aiohttp
            server.set_server_type('aiohttp')
            self.assertTrue(isinstance(server.get_app(), _aiohttp.Application))
        except ImportError:
            pass
        # here server type is the same as original one

    def test_invalid_server_type(self):
        with self.assertRaises(ValueError):
            server.set_server_type('a')


class TestServerBase(HTTPTestCase):
    cmd = []

    def setUp(self):
        super().setUp()
        self.port = free_port()
        env = os.environ.copy()
        env['PYTHONPATH'] = root
        _ = tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False)
        with _ as f:
            self.tmp = f.name
            f.write(script)
        cmd = [sys.executable, self.tmp, '--port', str(self.port)] + self.cmd
        self.url = 'http://localhost:{}'.format(self.port)
        self.ws_url = 'ws://localhost:{}/rimo_ws'.format(self.port)
        self.proc = subprocess.Popen(
            cmd, cwd=curdir, env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        sync(self.wait(times=10))

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)
        if self.proc.returncode is None:
            self.proc.terminate()
        sync(self.wait(times=10))
        super().tearDown()


class TestAutoShutdown(TestServerBase):
    cmd = ['--auto-shutdown', '--shutdown-wait', '0.1']

    @sync
    @asyncio.coroutine
    def test_autoshutdown(self):
        yield from self.wait()
        ws = yield from self.ws_connect(self.ws_url)
        ws.close()
        yield from self.wait(timeout=0.1, times=5)
        self.assertIsNotNone(self.proc.poll())

    @sync
    @asyncio.coroutine
    def test_reload(self):
        yield from self.wait()
        ws = yield from self.ws_connect(self.ws_url)
        ws.close()
        ws = yield from self.ws_connect(self.ws_url)
        yield from self.wait(timeout=0.1, times=5)
        self.assertIsNone(self.proc.poll())

    @sync
    @asyncio.coroutine
    def test_multi_connection(self):
        yield from self.wait()
        ws1 = yield from self.ws_connect(self.ws_url)
        ws2 = yield from self.ws_connect(self.ws_url)
        ws1.close()
        yield from self.wait(timeout=0.1, times=5)
        self.assertIsNone(self.proc.poll())
        ws2.close()
        yield from self.wait(timeout=0.1, times=5)
        self.assertIsNotNone(self.proc.poll())

    @sync
    @asyncio.coroutine
    def test_tempdir_cleanup(self):
        yield from self.wait()
        ws = yield from self.ws_connect(self.ws_url)
        resp = yield from self.fetch(self.url + '/tmp/a.html')
        content = resp.body
        self.assertTrue(path.exists(content.strip()))
        self.assertTrue(path.isdir(content.strip()))
        ws.close()
        yield from self.wait(timeout=0.1, times=5)
        self.assertIsNotNone(self.proc.poll())
        self.assertFalse(path.exists(content.strip()))
        self.assertFalse(path.isdir(content.strip()))


class TestOpenBrowser(TestServerBase):
    cmd = ['--debug', '--open-browser', '--browser', 'firefox']

    def test_open_browser(self):
        time.sleep(0.5)
        self.assertIn('Start server on', self.proc.stdout.readline())
        self.assertIn('connected', self.proc.stdout.readline())


class TestOpenBrowserFreePort(TestServerBase):
    cmd = ['--port', '0', '--open-browser', '--browser', 'firefox']

    def test_open_browser_free_port(self):
        time.sleep(0.5)
        self.assertIn('Start server on', self.proc.stdout.readline())
        self.assertIn('connected', self.proc.stdout.readline())


class TestMainHandlerBlank(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = get_document()
        self.start()

    @sync
    @asyncio.coroutine
    def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom', 'INFO'):
            res = yield from self.fetch(self.url)
        self.assertEqual(res.code, 200)
        _re = re.compile(
            '<!DOCTYPE html>\s*<html rimo_id="\d+">\s*<head rimo_id="\d+">'
            '.*<meta .*<title rimo_id="\d+">\s*W-DOM\s*</title>.*'
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
    @asyncio.coroutine
    def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom', 'INFO'):
            res = yield from self.fetch(self.url)
        self.assertEqual(res.code, 200)
        self.assertIn('testing', res.text)


class TestStaticFileHandler(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = get_document()
        self.start()

    @sync
    @asyncio.coroutine
    def test_static_file(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            res = yield from self.fetch(self.url + '/_static/js/rimo/rimo.js')
        self.assertEqual(res.code, 200)
        self.assertIn('rimo', res.text)
        self.assertIn('rimo.log', res.text)

    @sync
    @asyncio.coroutine
    def test_add_static_path(self) -> None:
        from os import path
        server.add_static_path('a', path.abspath(path.dirname(__file__)))
        with self.assertLogs('wdom.server', 'INFO'):
            res = yield from self.fetch(self.url + '/a/' + __file__)
        self.assertEqual(res.code, 200)
        self.assertIn('this text', res.text)

    @sync
    @asyncio.coroutine
    def test_tempdir(self):
        from os import path
        self.assertTrue(path.exists(self.document.tempdir))
        with self.assertLogs('wdom.server', 'INFO'):
            res = yield from self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(res.code, 404)
        self.assertIn('404', res.text)
        self.assertIn('Not Found', res.text)
        tmp = path.join(self.document.tempdir, 'a.html')
        with open(tmp, 'w') as f:
            f.write('test')
        self.assertTrue(path.exists(tmp))
        with self.assertLogs('wdom.server', 'INFO'):
            res = yield from self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(res.code, 200)
        self.assertEqual('test', res.text)

    @sync
    @asyncio.coroutine
    def test_tempfile(self):
        doc = get_document()
        self.assertTrue(path.exists(doc.tempdir))
        tmp = path.join(doc.tempdir, 'a.html')
        self.assertFalse(path.exists(tmp))
        with open(tmp, 'w') as f:
            f.write('test')
        self.assertTrue(path.exists(tmp))
        response = yield from self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.text, 'test')

    @sync
    @asyncio.coroutine
    def test_tempfile_404(self):
        response = yield from self.fetch(self.url + '/tmp/b.html')
        self.assertEqual(response.code, 404)
        response = yield from self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(response.code, 404)


class TestRootWSHandler(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.start()
        sync(self.wait())
        self.ws_url = 'ws://localhost:{}/rimo_ws'.format(self.port)
        self.ws = sync(self.ws_connect(self.ws_url))

    @sync
    @asyncio.coroutine
    def test_ws_connection(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            _ = yield from self.ws_connect(self.ws_url)
            del _
            yield from self.wait()

    @sync
    @asyncio.coroutine
    def test_logging_error(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='error', message='test')
            ))
            yield from self.wait()

    @sync
    @asyncio.coroutine
    def test_logging_warn(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='warn', message='test')
            ))
            yield from self.wait()

    @sync
    @asyncio.coroutine
    def test_logging_info(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='info', message='test')
            ))
            yield from self.wait()

    @sync
    @asyncio.coroutine
    def test_logging_debug(self) -> None:
        with self.assertLogs('wdom.server', 'DEBUG'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='debug', message='test')
            ))
            yield from self.wait()
