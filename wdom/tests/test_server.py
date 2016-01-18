#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import asyncio

from tornado.testing import AsyncHTTPTestCase, gen_test, ExpectLog
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future

from wdom.view import Document
from wdom.server import MainHandler, WSHandler, Application, get_app


def setup_module():
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
        with ExpectLog('wdom.server', 'connected'):
            with ExpectLog('wdom.server', '200 GET'):
                res = self.fetch('/')
        assert res.code == 200
        _re = re.compile('<!DOCTYPE html>\s*<head>.*<meta .*'
                         '<title>\s*W-DOM\s*</title>.*'
                         '</head>\s*<body.*>.*<script.*>.*</script>.*'
                         '</body>\s*</html>'
                         , re.S)
        assert _re.match(res.body.decode('utf8'))


class TestMainHandler(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.document.set_body('testing')
        self.app = Application(
            [('/', MainHandler)],
            document=self.document,
        )
        super().setUp()

    def get_app(self) -> None:
        return self.app

    def test_blank_mainpage(self) -> None:
        with ExpectLog('wdom.server', '.*connected'):
            with ExpectLog('wdom.server', '200 GET'):
                res = self.fetch('/')
        assert res.code == 200
        assert 'testing' in res.body.decode('utf8')


class TestStaticFileHandler(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.app = get_app(self.document)
        super().setUp()

    def get_app(self) -> None:
        return self.app

    def test_static_file(self) -> None:
        with ExpectLog('wdom.server', '200 GET'):
            res = self.fetch('/_static/js/wdom.js')
        assert res.code == 200
        assert 'Wlog' in res.body.decode('utf8')
        assert 'Wdom' in res.body.decode('utf8')

    def test_add_static_path(self) -> None:
        from os import path
        self.app.add_static_path('a', path.abspath(path.dirname(__file__)))
        with ExpectLog('wdom.server', '200 GET'):
            res = self.fetch('/a/' + __file__)
        assert res.code == 200
        assert 'this text' in res.body.decode('utf8')


class TestRootWSHandler(AsyncHTTPTestCase):
    def setUp(self) -> None:
        self.document = Document()
        self.app = get_app(self.document)
        super().setUp()
        self.url = self.get_url('/wdom_ws')

        with ExpectLog('wdom.server', 'WS OPEN'):
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
        with ExpectLog('wdom.server', 'WS OPEN'):
            ws = yield websocket_connect(self.url, io_loop=self.io_loop)

    def test_logging_error(self) -> None:
        with ExpectLog('wdom.server', 'JS: test'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='error', message='test')
            ))
            self.sleep()

    def test_logging_warn(self) -> None:
        with ExpectLog('wdom.server', 'JS: test'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='warn', message='test')
            ))
            self.sleep()

    def test_logging_info(self) -> None:
        with ExpectLog('wdom.server', 'JS: test'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='info', message='test')
            ))
            self.sleep()

    def test_logging_debug(self) -> None:
        with ExpectLog('wdom.server', 'JS: test'):
            self.ws.write_message(json.dumps(
                dict(type='log', level='debug', message='test')
            ))
            self.sleep()
