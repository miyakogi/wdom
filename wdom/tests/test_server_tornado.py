#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import asyncio

from syncer import sync

from wdom.misc import install_asyncio
from wdom.document import get_document
from wdom.server import get_app
from wdom import server
from wdom.testing import HTTPTestCase, suppress_logging


def setUpModule():
    install_asyncio()
    suppress_logging()


class TestMainHandlerBlank(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        server.set_server_type('tornado')
        self.document = get_document()
        self.app = get_app()
        self.start()

    @sync
    async def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom', 'INFO'):
            res = await self.fetch(self.url)
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
        server.set_server_type('tornado')
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
        server.set_server_type('tornado')
        self.document = get_document()
        self.start()

    @sync
    async def test_static_file(self) -> None:
        with self.assertLogs('wdom.server._tornado', 'INFO'):
            res = await self.fetch(self.url + '/_static/js/rimo/rimo.js')
        self.assertEqual(res.code, 200)
        self.assertIn('rimo', res.text)
        self.assertIn('rimo.log', res.text)

    @sync
    async def test_add_static_path(self) -> None:
        from os import path
        get_app().add_static_path('a', path.abspath(path.dirname(__file__)))
        with self.assertLogs('wdom.server._tornado', 'INFO'):
            res = await self.fetch(self.url + '/a/' + __file__)
        self.assertEqual(res.code, 200)
        self.assertIn('this text', res.text)

    @sync
    async def test_tempdir(self):
        from os import path
        self.assertTrue(path.exists(self.document.tempdir))
        with self.assertLogs('wdom.server._tornado', 'WARN'):
            res = await self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(res.code, 404)
        self.assertIn('404', res.text)
        self.assertIn('Not Found', res.text)
        tmp = path.join(self.document.tempdir, 'a.html')
        with open(tmp, 'w') as f:
            f.write('test')
        self.assertTrue(path.exists(tmp))
        with self.assertLogs('wdom.server._tornado', 'INFO'):
            res = await self.fetch(self.url + '/tmp/a.html')
        self.assertEqual(res.code, 200)
        self.assertEqual('test', res.text)


class TestRootWSHandler(HTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        server.set_server_type('tornado')
        self.start()
        sync(self.wait())
        self.ws_url = 'ws://localhost:{}/rimo_ws'.format(self.port)
        self.ws = sync(self.ws_connect(self.ws_url))

    async def wait(self, timeout=0.01):
        await asyncio.sleep(timeout)

    @sync
    async def test_ws_connection(self) -> None:
        with self.assertLogs('wdom.server._tornado', 'INFO'):
            _ = await self.ws_connect(self.ws_url)
            del _
            await self.wait()

    @sync
    async def test_logging_error(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='error', message='test')
            ))
            await self.wait()

    @sync
    async def test_logging_warn(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='warn', message='test')
            ))
            await self.wait()

    @sync
    async def test_logging_info(self) -> None:
        with self.assertLogs('wdom.server', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='info', message='test')
            ))
            await self.wait()

    @sync
    async def test_logging_debug(self) -> None:
        with self.assertLogs('wdom.server', 'DEBUG'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='debug', message='test')
            ))
            await self.wait()
