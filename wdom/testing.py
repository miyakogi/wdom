#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
import asyncio
import unittest
from multiprocessing import Process, Pipe
from types import FunctionType, MethodType

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.utils import free_port
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from tornado.httpclient import AsyncHTTPClient, HTTPResponse
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future
from tornado.websocket import websocket_connect, WebSocketClientConnection

from wdom.misc import install_asyncio
from wdom import options
from wdom.window import customElements
from wdom.element import Element
from wdom import server

driver = webdriver.Firefox
local_webdriver = None
remote_webdriver = None
browser_implict_wait = 0
logger = logging.getLogger(__name__)


def reset():
    '''Reset wdom objects. This function clear all connections, elements, and
    resistered custom elements. This function also makes new
    document/application and set them.
    '''
    from wdom.document import get_new_document, set_document
    from wdom.server import _aiohttp, _tornado
    set_document(get_new_document())
    _aiohttp.connections.clear()
    _tornado.connections.clear()
    _aiohttp.set_application(_aiohttp.Application())
    _tornado.set_application(_tornado.Application())
    Element._elements_with_id.clear()
    Element._elements.clear()
    customElements.clear()


def suppress_logging():
    options.root_logger.removeHandler(options._log_handler)
    options.root_logger.addHandler(logging.NullHandler())


class TestCase(unittest.TestCase):
    '''Base class for testing wdom modules. This class is a sub class of the
    ``unittest.TestCase``. After all test methods, reset wdom's global objects
    like document, application, and elements. If you use ``tearDown`` method,
    do not forget to call ``super().tearDown()``.

    If you want to reuse document/application object in your test class, please
    set them in each setup phase as follow::

        @classmethod
        def setUpClass(cls):
            cls.your_doc = get_document()
            cls.your_app = get_app()

        def setUp(self):
            from wdom.document import set_document
            from wdom.server import set_application
            set_document(self.your_doc)
            set_application(self.your_app)
    '''
    def tearDown(self):
        reset()
        super().tearDown()

    def assertIsTrue(self, bl):
        self.assertIs(bl, True)

    def assertIsFalse(self, bl):
        self.assertIs(bl, False)


class HTTPTestCase(TestCase):
    '''For http/ws connection test.'''
    _server_started = False

    def start(self):
        with self.assertLogs('wdom', 'INFO'):
            self.server = server.start_server(port=0)
        self.port = self.server.port
        self.url = 'http://localhost:{}'.format(self.port)
        self.ws_url = 'ws://localhost:{}'.format(self.port)
        self._server_started = True

    def tearDown(self):
        if self._server_started:
            with self.assertLogs('wdom', 'INFO'):
                server.stop_server(self.server)
            self._server_started = False
        super().tearDown()

    @asyncio.coroutine
    def fetch(self, url: str, encoding: str = 'utf-8') -> HTTPResponse:
        '''Fetch url. Response body is decoded by ``encoding`` and set
        ``text`` property of the response. If failed to decode, ``text``
        property will set to ``None``.
        '''
        response = yield from to_asyncio_future(
            AsyncHTTPClient().fetch(url, raise_error=False))
        try:
            response.text = response.body.decode(encoding)
        except UnicodeDecodeError:
            response.text = None
        return response

    @asyncio.coroutine
    def ws_connect(self, url: str, _retry=0, _max=20, _wait=0.05
                   ) -> WebSocketClientConnection:
        '''Make WebSocket connection to the url.'''
        try:
            ws = yield from to_asyncio_future(websocket_connect(url))
        except ConnectionRefusedError:
            if _retry <= _max:
                yield from asyncio.sleep(_wait)
                ws = yield from self.ws_connect(url, _retry+1, _max, _wait)
            else:
                raise ConnectionRefusedError(
                    'WebSocket connection refused: {}'.format(url))
        return ws


def start_webdriver():
    '''Start WebDriver and set implicit_wait if it is not started.'''
    global local_webdriver
    if local_webdriver is None:
        local_webdriver = driver()
        if browser_implict_wait:
            local_webdriver.implicitly_wait(browser_implict_wait)


def close_webdriver():
    '''Close WebDriver.'''
    global local_webdriver
    if local_webdriver is not None:
        local_webdriver.close()
        local_webdriver = None


def get_webdriver():
    '''Return WebDriver of current process. If it is not started, start and
    return it.'''
    if globals().get('local_webdriver') is None:
        start_webdriver()
    return local_webdriver


def _clear():
    global conn, wd_conn, browser_manager, remote_webdriver
    conn = None
    wd_conn = None
    browser_manager = None
    remote_webdriver = None


def start_remote_browser():
    '''Start WebDriver on remote process.'''
    global browser_manager, conn, wd_conn
    conn, wd_conn = Pipe()

    def start_browser():
        global wd_conn
        bc = BrowserController(wd_conn)
        bc.run()

    browser_manager = Process(target=start_browser)
    browser_manager.start()


def close_remote_browser():
    '''Terminate browser process.'''
    global conn, browser_manager
    conn.send({'target': 'process', 'method': 'quit'})
    time.sleep(0.3)
    logger.info('\nRemote Browser closed')
    conn.close()
    if browser_manager is not None:
        browser_manager.terminate()
    _clear()


def get_remote_browser():
    '''Start new WebDriver for remote process.'''
    global remote_webdriver
    if remote_webdriver is None:
        remote_webdriver = driver()
        if browser_implict_wait:
            remote_webdriver.implicitly_wait(browser_implict_wait)
        return remote_webdriver
    else:
        return remote_webdriver


class BrowserController:
    '''Class to run webdriver in different proceess. Inter-process
    communication is done via Pipe.
    '''
    _select_methods = [s for s in dir(Select) if not s.startswith('_')]

    def __init__(self, conn):
        '''Set up connection and start webdriver. ``conn`` is a one end of
        ``Pipe()``, which is used the inter-process communication.
        '''
        self.conn = conn
        self.wd = get_remote_browser()
        self.element = None

    def set_element_by_id(self, id):
        '''Find element with ``id`` and set it as operation target. When
        successfully find the element, send ``True``. If failed to find the
        element, send message ``Error NoSuchElement: {{ id }}``.'''
        try:
            self.element = self.wd.find_element_by_css_selector(
                '[rimo_id="{}"]'.format(id))
            return True
        except NoSuchElementException:
            return 'Error NoSuchElement: ' + id

    def quit(self, *args):
        self.wd.quit()
        return 'closed'

    def close(self, *args):
        self.wd.close()
        return 'closed'

    def _execute_method(self, method, args):
        if isinstance(method, (FunctionType, MethodType)):
            self.conn.send(method(*args))
        else:
            # not callable, just send it back
            self.conn.send(method)

    def run(self):
        '''Running process. Wait message from the other end of the connection,
        and when gat message, execute the method specified by the message.
        The message is a python's dict, which must have ``method`` field.
        '''
        while True:
            req = self.conn.recv()
            target = req.get('target', '')
            method_name = req.get('method', '')
            args = req.get('args', [])
            if target == 'process':
                method = getattr(self, method_name)
            elif target == 'browser':
                method = getattr(self.wd, method_name)
            elif target == 'element':
                if self.element is None:
                    # Element must be set
                    self.conn.send('Error: No Element Set')
                    continue
                if (method_name in self._select_methods and
                        self.element.tag_name.lower() == 'select'):
                    s = Select(self.element)
                    method = getattr(s, method_name)
                else:
                    method = getattr(self.element, method_name)
            self._execute_method(method, args)


def wait_for():
    '''Wait the action doing in the browser process, and afer finish it,
    return the value.'''
    return asyncio.get_event_loop().run_until_complete(wait_coro())


@asyncio.coroutine
def wait_coro():
    while True:
        state = conn.poll()
        if state:
            res = conn.recv()
            return res
        else:
            yield from asyncio.sleep(0)
            continue


def _get_properties(cls):
    props = set()
    for k, v in vars(cls).items():
        if not isinstance(v, (FunctionType, MethodType)):
            props.add(k)
    return props


class Controller:
    target = None
    properties = set()

    def __getattr__(self, attr: str):
        global conn

        def wrapper(*args):
            conn.send({'target': self.target, 'method': attr, 'args': args})
            res = wait_for()
            if isinstance(res, str):
                if res.startswith('Error NoSuchElement'):
                    raise NoSuchElementException(res)
                elif res.startswith('Error'):
                    raise ValueError(res)
            return res
        if attr in self.properties:
            return wrapper()
        else:
            return wrapper


class ProcessController(Controller):
    target = 'process'


class RemoteBrowserController(Controller):
    target = 'browser'
    properties = _get_properties(WebDriver)


class RemoteElementController(Controller):
    target = 'element'
    properties = _get_properties(WebElement)


class RemoteBrowserTestCase:
    '''This class is **Experimental**.

    Utility class for testing apps with webdriver in another process. Mainly
    used for development and test of wdom library itself. This class does not
    support all methods provided by selenium.webdriver, but maybe enough.

    Usage:

    Make subclass and override ``get_app`` method to return app (instance of
    ``wdom.server.Application`` or ``tornado.web.Application``), which you want
    to test.
    '''
    wait_time = 0.1 if os.environ.get('TRAVIS', False) else 0.02

    def start(self):
        self._prev_logging = options.config.logging
        options.config.logging = 'warn'
        self.proc = ProcessController()
        self.browser = RemoteBrowserController()
        self.element = RemoteElementController()
        try:
            self.server = server.start_server(port=0)
        except OSError:
            self.wait(0.2)
            self.server = server.start_server(port=0)
        self.address = self.server.address
        self.url = 'http://{0}:{1}/'.format(self.address, self.port)
        self.wait()
        self.browser.get(self.url)
        self.wait()

    def tearDown(self):
        options.config.logging = self._prev_logging
        self.stop_server()
        self.wait()
        sys.stdout.flush()
        sys.stderr.flush()
        super().tearDown()

    @property
    def port(self) -> int:
        return self.server.port

    def stop_server(self):
        server.stop_server(self.server)

    def wait(self, timeout=None):
        '''Wait until ``timeout``. The default timeout is zero, so wait a
        single event loop. This method does not block the thread, so the server
        in test still can send response before timeout.
        '''
        asyncio.get_event_loop().run_until_complete(
            asyncio.sleep(timeout or self.wait_time))

    def set_element(self, node):
        '''Wrapper method of ``set_element_by_id``. Set the ``node`` as a
        target node of the browser process.'''
        return self.proc.set_element_by_id(node.rimo_id)


class WebDriverTestCase:
    '''Base class for testing UI on browser. This class starts up an HTTP
    server on a new subprocess.

    Subclasses must override ``get_app()`` method, which returns the
    ``pygmariot.server.Application`` or ``tornado.web.Application`` to be
    tested.
    '''
    wait_time = 0.1 if os.environ.get('TRAVIS', False) else 0.02

    @classmethod
    def setUpClass(cls):
        cls._orig_loop = asyncio.get_event_loop()
        # Need to use different loop for aiohttp after remote_browser tests
        # but I can't understand why...?
        asyncio.set_event_loop(asyncio.new_event_loop())
        # When change default loop, tornado's ioloop needs to be reinstalled
        AsyncIOMainLoop().clear_current()
        AsyncIOMainLoop().clear_instance()
        install_asyncio()

    @classmethod
    def tearDownClass(cls):
        # Set original loop and reinstall to tornado
        asyncio.set_event_loop(cls._orig_loop)
        AsyncIOMainLoop().clear_current()
        AsyncIOMainLoop().clear_instance()
        install_asyncio()

    def start(self):
        self.wd = get_webdriver()

        def start_server(port):
            import asyncio
            from wdom import server
            server.start_server(port=port)
            asyncio.get_event_loop().run_forever()

        self.address = 'localhost'
        self.port = free_port()
        self.url = 'http://{0}:{1}/'.format(self.address, self.port)

        self.server = Process(
            target=start_server,
            args=(self.port, )
        )
        self.server.start()
        self.wait(0.1)
        self.wd.get(self.url)
        self.wait(0.05)

    def tearDown(self):
        '''Terminate server subprocess.'''
        self.server.terminate()
        sys.stdout.flush()
        sys.stderr.flush()
        super().tearDown()

    def get_app(self):
        '''This method should be overridden. Return
        ``pygmariot.server.Application`` or ``tornado.web.Application`` to be
        tested.
        '''
        NotImplementedError

    def wait(self, timeout=None):
        '''Wait until ``timeout``. The default timeout is zero, so wait a
        single event loop.'''
        time.sleep(timeout or self.wait_time)

    def send_keys(self, element, keys: str):
        '''Send ``keys`` to ``element`` one-by-one. Safer than using
        ``element.send_keys`` method.
        '''
        for k in keys:
            element.send_keys(k)
