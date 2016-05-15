#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
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
    """Reset all wdom objects.

    This function clear all connections, elements, and resistered custom
    elements. This function also makes new document/application and set them.
    """
    from wdom.document import get_new_document, set_document
    set_document(get_new_document())
    from wdom.server import _tornado
    _tornado.connections.clear()
    _tornado.set_application(_tornado.Application())
    try:
        from wdom.server import _aiohttp
        _aiohttp.connections.clear()
        _aiohttp.set_application(_aiohttp.Application())
    except ImportError:
        pass
    Element._elements_with_id.clear()
    Element._elements.clear()
    customElements.clear()


def suppress_logging():
    """Suppress log output to stdout.

    This function is intended to be used in test's setup. This function removes
    log handler of ``wdom`` logger and set NullHandler to suppress log.
    """
    options.root_logger.removeHandler(options._log_handler)
    options.root_logger.addHandler(logging.NullHandler())


class TestCase(unittest.TestCase):
    """Base class for testing wdom modules.

    This class is a sub class of the ``unittest.TestCase``. After all test
    methods, reset wdom's global objects like document, application, and
    elements. If you use ``tearDown`` method, do not forget to call
    ``super().tearDown()``.

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
    """

    def tearDown(self):
        reset()
        super().tearDown()

    def assertIsTrue(self, bl):
        """Check arg is exactly True, not truthy."""
        self.assertIs(bl, True)

    def assertIsFalse(self, bl):
        """Check arg is exactly False, not falsy."""
        self.assertIs(bl, False)


class HTTPTestCase(TestCase):
    """For http/ws connection test."""

    wait_time = 0.01
    timeout = 1.0
    _server_started = False
    _ws_connections = []

    def start(self):
        """Start web server.

        Please call this method after prepraring document.
        """
        with self.assertLogs('wdom', 'INFO'):
            self.server = server.start_server(port=0)
        self.port = self.server.port
        self.url = 'http://localhost:{}'.format(self.port)
        self.ws_url = 'ws://localhost:{}'.format(self.port)
        self._server_started = True

    def tearDown(self):
        """Terminate server and close all ws client connections."""
        if self._server_started:
            with self.assertLogs('wdom', 'INFO'):
                server.stop_server(self.server)
            self._server_started = False
        while self._ws_connections:
            ws = self._ws_connections.pop()
            ws.close()
        super().tearDown()

    @asyncio.coroutine
    def fetch(self, url: str, encoding: str = 'utf-8') -> HTTPResponse:
        """Fetch url and return ``tornado.httpclient.HTTPResponse`` object.

        Response body is decoded by ``encoding`` and set ``text`` property of
        the response. If failed to decode, ``text`` property will be ``None``.
        """
        response = yield from to_asyncio_future(
            AsyncHTTPClient().fetch(url, raise_error=False))
        try:
            response.text = response.body.decode(encoding)
        except UnicodeDecodeError:
            response.text = None
        return response

    @asyncio.coroutine
    def ws_connect(self, url: str, timeout: float = None
                   ) -> WebSocketClientConnection:
        """Make WebSocket connection to the url.

        Retries up to _max (default: 20) times. Client connections made by this
        method are closed after each test method.
        """
        st = time.perf_counter()
        timeout = timeout or self.timeout
        while (time.perf_counter() - st) < timeout:
            try:
                ws = yield from to_asyncio_future(websocket_connect(url))
            except ConnectionRefusedError:
                yield from self.wait()
                continue
            else:
                self._ws_connections.append(ws)
                return ws
        raise ConnectionRefusedError(
            'WebSocket connection refused: {}'.format(url))

    @asyncio.coroutine
    def wait(self, timeout: float = None, times: int = 1):
        """Coroutine to wait for ``timeout``.

        ``timeout`` is second to wait, and its default value is
        ``self.wait_time``. If ``times`` are specified, wait for
        ``timeout * times``.
        """
        for i in range(times):
            yield from asyncio.sleep(timeout or self.wait_time)


def start_webdriver():
    """Start WebDriver and set implicit_wait if it is not started."""
    global local_webdriver
    if local_webdriver is None:
        local_webdriver = driver()
        if browser_implict_wait:
            local_webdriver.implicitly_wait(browser_implict_wait)


def close_webdriver():
    """Close WebDriver."""
    global local_webdriver
    if local_webdriver is not None:
        local_webdriver.close()
        local_webdriver = None


def get_webdriver():
    """Return WebDriver of current process.

    If it is not started yet, start and return it.
    """
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
    """Start remote browser process."""
    global browser_manager, conn, wd_conn
    conn, wd_conn = Pipe()

    def start_browser():
        global wd_conn
        bc = BrowserController(wd_conn)
        bc.run()

    browser_manager = Process(target=start_browser)
    browser_manager.start()


def close_remote_browser():
    """Terminate remote browser process."""
    global conn, browser_manager
    conn.send({'target': 'process', 'method': 'quit'})
    time.sleep(0.3)
    logger.info('\nRemote Browser closed')
    conn.close()
    if browser_manager is not None:
        browser_manager.terminate()
    _clear()


def get_remote_browser():
    """Start new WebDriver for remote process."""
    global remote_webdriver
    if remote_webdriver is None:
        remote_webdriver = driver()
        if browser_implict_wait:
            remote_webdriver.implicitly_wait(browser_implict_wait)
        return remote_webdriver
    else:
        return remote_webdriver


class BrowserController:
    """Class to run and wrap webdriver in different proceess.
    """
    _select_methods = [s for s in dir(Select) if not s.startswith('_')]

    def __init__(self, conn):
        """Set up connection and start webdriver.

        ``conn`` is a one end of ``Pipe()``, which is used the inter-process
        communication.
        """
        self.conn = conn
        self.wd = get_remote_browser()
        self.element = None

    def set_element_by_id(self, id):
        """Find element with ``id`` and set it to element property.

        When successfully find the element, send ``True``. If failed to find the
        element, send message ``Error NoSuchElement: {{ id }}``.
        """
        try:
            self.element = self.wd.find_element_by_css_selector(
                '[rimo_id="{}"]'.format(id))
            return True
        except NoSuchElementException:
            return 'Error NoSuchElement: ' + id

    def quit(self, *args):
        """Terminate WebDriver."""
        self.wd.quit()
        return 'closed'

    def close(self, *args):
        """Close WebDriver."""
        self.wd.close()
        return 'closed'

    def _execute_method(self, method, args):
        if isinstance(method, (FunctionType, MethodType)):
            self.conn.send(method(*args))
        else:
            # not callable, just send it back
            self.conn.send(method)

    def run(self):
        """Wait message from the other end of the connection.

        When gat message, execute the method specified by the message. The
        message should be a python's dict, which must have ``target`` and
        ``method`` field.
        """
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
    """Wait the response from the remote process and return it."""
    return asyncio.get_event_loop().run_until_complete(wait_coro())


@asyncio.coroutine
def wait_coro():
    """Wait response from the other process."""
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
    """Base class for remote browser controller."""
    target = None
    properties = set()

    def __getattr__(self, attr: str):
        """Call methods related to this controller."""
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
    """Controller of remote browser process."""
    target = 'process'


class RemoteBrowserController(Controller):
    """Controller of remote web driver."""
    target = 'browser'
    properties = _get_properties(WebDriver)


class RemoteElementController(Controller):
    """Controller of remote web driver element."""
    target = 'element'
    properties = _get_properties(WebElement)


class TimeoutError(Exception):
    """The operation is not completed by timeout."""


class RemoteBrowserTestCase:
    """This class is **Experimental**.

    Utility class for testing apps with webdriver in another process. Mainly
    used for development and test of wdom library itself. This class does not
    support all methods provided by selenium.webdriver, but maybe enough.

    After seting up your document, call ``start`` method in setup sequence.
    """
    #: seconds to wait for by ``wait`` method.
    wait_time = 0.01
    #: secondes for deault timeout for ``wait_until`` method
    timeout = 1.0

    def start(self):
        """Start remote browser process."""
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
        self.browser.get(self.url)
        self.wait_until(lambda: server.is_connected())

    def tearDown(self):
        options.config.logging = self._prev_logging
        server.stop_server()
        sys.stdout.flush()
        sys.stderr.flush()
        super().tearDown()

    @property
    def port(self) -> int:
        """Get port of the server."""
        return self.server.port

    def wait(self, timeout: float = None, times: int = 1):
        """Wait for ``timeout`` seconds.

        Default timeout is ``RemoteBrowserTestCase.wait_time``.
        """
        loop = asyncio.get_event_loop()
        for i in range(times):
            loop.run_until_complete(asyncio.sleep(timeout or self.wait_time))

    def wait_until(self, func, timeout=None):
        """Wait until ``func`` returns True or exceeds timeout.

        ``func`` is called with no argument. Unit of ``timeout`` is second, and
        its default value is RemoteBrowserTestCase.timeout class variable
        (default: 1.0).
        """
        st = time.perf_counter()
        timeout = timeout or self.timeout
        while (time.perf_counter() - st) < timeout:
            if func():
                return
            self.wait()
        raise TimeoutError('{} did not return True until timeout'.format(func))

    def _set_element(self, node):
        try:
            res = self.proc.set_element_by_id(node.rimo_id)
            return res
        except NoSuchElementException:
            return False

    def set_element(self, node, timeout=None):
        """Set the ``node`` as a target node of the remote browser process."""
        try:
            self.wait_until(lambda: self._set_element(node), timeout)
            return True
        except TimeoutError:
            pass
        raise NoSuchElementException('element not found: {}'.format(node))


class WebDriverTestCase:
    """Base class for testing UI on browser.

    This class starts up an HTTP server on a new subprocess.

    Subclasses should call ``start`` method after seting up your document.
    After ``start`` method called, the web server is running on the other
    process so you cannot make change on the document. If you need to change
    document after server started, please use ``RemoteBrowserTestCase`` class
    instead.
    """
    #: seconds to wait for by ``wait`` method.
    wait_time = 0.01
    #: secondes for deault timeout for ``wait_until`` method
    timeout = 1.0

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
        reset()

    @classmethod
    def tearDownClass(cls):
        # Set original loop and reinstall to tornado
        asyncio.set_event_loop(cls._orig_loop)
        AsyncIOMainLoop().clear_current()
        AsyncIOMainLoop().clear_instance()
        install_asyncio()
        reset()

    def start(self):
        """Start server and web driver."""
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
        self.wait(times=10)
        self.wd.get(self.url)

    def tearDown(self):
        """Terminate server subprocess."""
        self.server.terminate()
        sys.stdout.flush()
        sys.stderr.flush()
        self.wait(times=10)
        super().tearDown()

    def wait(self, timeout: float = None, times: int = 1):
        """Wait for ``timeout`` or ``self.wait_time``."""
        loop = asyncio.get_event_loop()
        for i in range(times):
            loop.run_until_complete(asyncio.sleep(timeout or self.wait_time))

    def wait_until(self, func, timeout=None):
        """Wait until ``func`` returns True or exceeds timeout.

        ``func`` is called with no argument. Unit of ``timeout`` is second, and
        its default value is RemoteBrowserTestCase.timeout class variable
        (default: 1.0).
        """
        st = time.perf_counter()
        timeout = timeout or self.timeout
        while (time.perf_counter() - st) < timeout:
            if func():
                return
            self.wait()
        raise TimeoutError('{} did not return True until timeout'.format(func))

    def send_keys(self, element, keys: str):
        """Send ``keys`` to ``element`` one-by-one.

        Safer than using ``element.send_keys`` method.
        """
        for k in keys:
            element.send_keys(k)
