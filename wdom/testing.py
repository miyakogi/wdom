#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import asyncio
import socket
import unittest
from multiprocessing import Process, Pipe
from types import FunctionType, MethodType

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.utils import free_port

from tornado.web import Application
from tornado.httpserver import HTTPServer

from wdom.misc import static_dir
from wdom import options

driver = webdriver.Firefox


class TestCase(unittest.TestCase):
    def assertIsTrue(self, bl):
        self.assertIs(bl, True)

    def assertIsFalse(self, bl):
        self.assertIs(bl, False)


def start_webdriver():
    if globals().get('local_webdriver') is None:
        global local_webdriver
        local_webdriver = driver()


def close_webdriver():
    if globals().get('local_webdriver') is not None:
        global local_webdriver
        local_webdriver.close()
        local_webdriver = None


def get_webdriver():
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
    '''Start broser process.'''
    _clear()
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
    print('\nRemote Browser closed')
    conn.close()
    if browser_manager is not None:
        browser_manager.terminate()
    _clear()


def get_remote_browser():
    '''Get existing webdriver. If no driver is running, start new one.'''
    remote_webdriver = globals().get('remote_webdriver')
    if remote_webdriver is None:
        remote_webdriver = driver()
        return remote_webdriver
    else:
        return remote_webdriver


class BrowserController:
    '''Class to run webdriver in different proceess. Inter-process
    communication is done via Pipe.
    '''
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
            yield from asyncio.sleep(0.01)
            continue

class Controller:
    target = None
    def __getattr__(self, attr:str):
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
        return wrapper


class ProcessController(Controller):
    target = 'process'


class RemoteBrowserController(Controller):
    target = 'browser'
    @property
    def page_source(self) -> str:
        return super().__getattr__('page_source')()


class RemoteElementController(Controller):
    target = 'element'
    @property
    def text(self) -> str:
        return super().__getattr__('text')()


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
    from wdom import server
    module = server
    wait_time = 0.02

    def setUp(self):
        self._prev_logging = options.config.logging
        options.config.logging = 'WARN'
        self.proc = ProcessController()
        self.browser = RemoteBrowserController()
        self.element = RemoteElementController()
        self.address = 'localhost'
        self.app = self.get_app(self.document)
        self.app.add_favicon_path(static_dir)
        self.start_server(self.app)
        self.url = 'http://{0}:{1}/'.format(self.address, self.port)
        super().setUp()
        self.wait()
        self.browser.get(self.url)
        self.wait()

    def teardown(self):
        options.config.logging = self._prev_logging
        self.stop_server()
        self.wait()

    @property
    def port(self) -> int:
        if isinstance(self.server, HTTPServer):
            for sock in self.server._sockets.values():
                if sock.family == socket.AF_INET:
                    return sock.getsockname()[1]
        elif isinstance(self.server, asyncio.AbstractServer):
            return self.server.sockets[-1].getsockname()[1]

    def start_server(self, app, port=0):
        try:
            self.server = self.module.start_server(app, port)
        except OSError:
            self.wait(0.2)
            self.server = self.module.start_server(app, port)

    def stop_server(self):
        self.module.stop_server(self.server)

    def get_app(self, doc=None) -> Application:
        '''This method should be overridden by subclasses. Return
        ``wdom.server.Application`` (subclass of ``tornado.web.Application``)
        or ``asyncio.Server`` to be tested.
        '''
        return self.module.get_app(doc)

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
    from wdom import server_aio
    module = server_aio
    wait_time = 0.02

    def setUp(self):
        self.wd = get_webdriver()
        self.loop = asyncio.get_event_loop()

        def start_server(app, port):
            self.module.start_server(app, port=port)
            asyncio.get_event_loop().run_forever()

        self.address = 'localhost'
        self.port = free_port()
        self.app = self.get_app()
        self.url = 'http://{0}:{1}/'.format(self.address, self.port)

        self.server = Process(
            target=start_server,
            args=(self.app, self.port)
        )
        self.server.start()
        self.wait(0.1)
        self.wd.get(self.url)
        self.wait(0.05)

    def tearDown(self):
        '''Terminate server subprocess.'''
        self.server.terminate()

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
