#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future

from wdom.document import Document
from wdom.server_tornado import MainHandler, Application, get_app


def setUpModule():
    if not IOLoop.initialized():
        AsyncIOMainLoop().install()
    import logging
    from wdom.log import configure_logger
    configure_logger(logging.DEBUG)


class TestMainHandlerBlank(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.app = Application(
            [('/', MainHandler)],
            document=self.document,
        )
        super().setUp()

    def get_app(self) -> None:
        return self.app

    def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom.server_tornado', 'INFO'):
            res = self.fetch('/')
        self.assertEqual(res.code, 200)
        _re = re.compile('<!DOCTYPE html>\s*<html rimo_id="\d+">\s*<head rimo_id="\d+">'
                         '.*<meta .*<title rimo_id="\d+">\s*W-DOM\s*</title>.*'
                         '</head>\s*<body.*>.*<script.*>.*</script>.*'
                         '</body>\s*</html>'
                         , re.S)
        self.assertIsNotNone(_re.match(res.body.decode('utf8')))


class TestMainHandler(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.document.body.prepend('testing')
        self.app = Application(
            [('/', MainHandler)],
            document=self.document,
        )
        super().setUp()

    def get_app(self) -> None:
        return self.app

    def test_blank_mainpage(self) -> None:
        with self.assertLogs('wdom.server_tornado', 'INFO'):
            res = self.fetch('/')
        self.assertEqual(res.code, 200)
        self.assertIn('testing', res.body.decode('utf8'))


class TestStaticFileHandler(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.app = get_app(self.document)
        super().setUp()

    def get_app(self) -> None:
        return self.app

    def test_static_file(self) -> None:
        with self.assertLogs('wdom.server_tornado', 'INFO'):
            res = self.fetch('/_static/js/rimo/rimo.js')
        self.assertEqual(res.code, 200)
        body = res.body.decode('utf8')
        self.assertIn('rimo', body)
        self.assertIn('rimo.log', body)

    def test_add_static_path(self) -> None:
        from os import path
        self.app.add_static_path('a', path.abspath(path.dirname(__file__)))
        with self.assertLogs('wdom.server_tornado', 'INFO'):
            res = self.fetch('/a/' + __file__)
        self.assertEqual(res.code, 200)
        self.assertIn('this text', res.body.decode('utf8'))


class TestRootWSHandler(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.app = get_app(self.document)
        super().setUp()
        self.url = self.get_url('/rimo_ws')

        with self.assertLogs('wdom.server_tornado', 'INFO'):
            ws_future = to_asyncio_future(websocket_connect(
                self.url, callback=self.stop))
            self.wait()
            self.ws = ws_future.result()

    def get_app(self) -> None:
        return self.app

    def get_protocol(self) -> str:
        return 'ws'

    def sleep(self, timeout=0.01) -> None:
        try:
            self.wait(timeout=timeout)
        except AssertionError:
            pass

    @gen_test
    def test_ws_connection(self) -> None:
        with self.assertLogs('wdom.server_tornado', 'INFO'):
            _ = yield websocket_connect(self.url, io_loop=self.io_loop)
            del _

    def test_logging_error(self) -> None:
        with self.assertLogs('wdom.handler', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='error', message='test')
            ))
            self.sleep()

    def test_logging_warn(self) -> None:
        with self.assertLogs('wdom.handler', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='warn', message='test')
            ))
            self.sleep()

    def test_logging_info(self) -> None:
        with self.assertLogs('wdom.handler', 'INFO'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='info', message='test')
            ))
            self.sleep()

    def test_logging_debug(self) -> None:
        with self.assertLogs('wdom.handler', 'DEBUG'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='debug', message='test')
            ))
            self.sleep()
