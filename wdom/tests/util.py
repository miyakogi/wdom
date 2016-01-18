#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''

import time
import asyncio
from multiprocessing import Process, Pipe
from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.common.utils import free_port
from selenium.common.exceptions import NoSuchElementException

from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop

from wdom.server import start_server

driver = webdriver.Firefox
wd = None
conn, wd_conn = Pipe()
browser = None


def install_asyncio():
    '''Ensure asyncio's io-loop is installed to tornado.'''
    if not IOLoop.initialized():
        AsyncIOMainLoop().install()


def setup_module():
    '''Install asyncio's io-loop to tornado and start Selenium WebDriver
    process.'''
    install_asyncio()
    start_browser()


def teardown_module():
    '''Close Selenium WebDriver process.'''
    close_browser()


def get_browser():
    '''Get existing webdriver. If no driver is running, start new one.'''
    global wd
    if wd is None:
        wd = webdriver.Firefox()
        return wd
    else:
        return wd


class BrowserController:
    '''Class to run webdriver in different proceess. Inter-process
    communication is done via Pipe.
    '''
    def __init__(self, conn):
        '''Set up connection and start webdriver. ``conn`` is a one end of
        ``Pipe()``, which is used the inter-process communication.
        '''
        self.conn = conn
        self.wd = get_browser()
        self.element = None

    def get(self, url):
        '''Open url. When page has been loaded, send ``True``.'''
        self.wd.get(url)
        self.conn.send(True)

    def set_element_by_id(self, id):
        '''Find element with ``id`` and set it as operation target. When
        successfully find the element, send ``True``. If failed to find the
        element, send message ``Error NoSuchElement: {{ id }}``.'''
        try:
            self.element = self.wd.find_element_by_id(id)
            self.conn.send(True)
        except NoSuchElementException:
            self.conn.send('Error NoSuchElement: ' + id)

    def get_attribute(self, attr) -> str:
        '''Get ``attr`` of the target element. If succeed to get, send the
        value. The target element does not has the attribute, send ``None``
        (deafult by selenium).
        '''
        if self.element is not None:
            self.conn.send(self.element.get_attribute(attr))
        else:
            self.conn.send('No Element Set')

    def get_text(self) -> str:
        '''Get text content of the target element and send it.'''
        if self.element is not None:
            text = self.element.text
            self.conn.send(text)
        else:
            self.conn.send('No Element Set')

    def is_displayed(self) -> bool:
        '''Return if the target element is visible for user or not.'''
        if self.element is not None:
            res = self.element.is_displayed()
            self.conn.send(res)
        else:
            self.conn.send('No Element Set')

    def click(self) -> None:
        if self.element is not None:
            res = self.element.click()
            self.conn.send(res)
        else:
            self.conn.send('No Element Set')

    def send_keys(self, keys: str) -> None:
        if self.element is not None:
            for s in keys:
                self.element.send_keys(s)
            self.conn.send(True)
        else:
            self.conn.send('No Element Set')

    def run(self):
        '''Running process. Wait message from the other end of the connection,
        and when gat message, execute the method specified by the message.
        The message is a python's dict, which must have ``method`` field.
        '''
        while True:
            req = self.conn.recv()
            if req['method'] == 'get':
                self.get(req['url'])
            elif req['method'] == 'set_element_by_id':
                self.set_element_by_id(req['id'])
            elif req['method'] == 'get_attribute':
                self.get_attribute(req['attr'])
            elif req['method'] == 'get_text':
                self.get_text()
            elif req['method'] == 'is_displayed':
                self.is_displayed()
            elif req['method'] == 'click':
                self.click()
            elif req['method'] == 'send_keys':
                self.send_keys(req['keys'])
            elif req['method'] == 'close':
                self.wd.close()
                self.conn.send('CLOSED')
                break


def start_browser():
    '''Start broser process.'''
    global browser
    def start_browser():
        global wd_conn
        bc = BrowserController(wd_conn)
        bc.run()

    browser = Process(target=start_browser)
    browser.start()


def close_browser():
    '''Terminate browser process.'''
    global conn, browser
    conn.send({'method': 'close'})
    time.sleep(0.3)
    print('\nBrowser closed')
    conn.close()
    if browser is not None:
        browser.terminate()


class WDTest(TestCase):
    '''This class is **Experimental**.

    Utility class for testing apps with webdriver in another process. Mainly
    used for development and test of wdom library itself. This class does not
    support all methods provided by selenium.webdriver, but maybe enough.

    Usage:

    Make subclass and override ``get_app`` method to return app (instance of
    ``wdom.server.Application`` or ``tornado.web.Application``), which you wand
    to test.
    '''
    def setUp(self):
        global conn
        self.conn = conn
        self.loop = asyncio.get_event_loop()
        self.address = 'localhost'
        self.port = free_port()
        self.app = self.get_app()
        self.url = 'http://{0}:{1}/'.format(self.address, self.port)
        self.server = start_server(self.app, self.port)
        # super().setUp()
        self.wait(0.1)
        self.get(self.url)
        self.wait(0.1)

    def tearDown(self):
        self.server.stop()

    def get_app(self) -> Application:
        '''This method should be overridden by subclasses. Return
        ``pygmariot.server.Application``, ``tornado.web.Application`` to be
        tested.
        '''
        NotImplementedError

    def get(self, url):
        '''Load the url by browser.'''
        self.conn.send({'method': 'get', 'url': url})
        return self.wait_for()

    def wait(self, timeout=0.0):
        '''Wait until ``timeout``. The default timeout is zero, so wait a
        single event loop. This method does not block the thread, so the server
        in test still can send response before timeout.
        '''
        self.loop.run_until_complete(asyncio.sleep(timeout))

    def wait_for(self):
        '''Wait the action doing in the browser process, and afer finish it,
        return the value.'''
        return self.loop.run_until_complete(self.wait_coro())

    @asyncio.coroutine
    def wait_coro(self):
        while True:
            state = self.conn.poll()
            if state:
                res = self.conn.recv()
                return res
            else:
                yield from asyncio.sleep(0.01)
                continue

    def set_element(self, node):
        '''Wrapper method of ``set_element_by_id``. Set the ``node`` as a
        target node of the browser process.'''
        return self.set_element_by_id(node.id)

    def set_element_by_id(self, id):
        '''Set the ``node`` specified by ``id`` as a target element of the
        broser process. If no element which has the id is not found, in
        browser, raise ``selenium.common.exceptions.NoSuchElementException``.
        '''
        self.conn.send({'method': 'set_element_by_id', 'id': id})
        res = self.wait_for()
        if res is True:
            return res
        elif res.startswith('Error NoSuchElement'):
            raise NoSuchElementException(res)
        else:
            return res

    def get_attribute(self, attr) -> str:
        '''Get the attribute's value of the target element. If the current
        target element does not have the attribute, return ``None``.'''
        self.conn.send({'method': 'get_attribute', 'attr': attr})
        return self.wait_for()

    def get_text(self) -> str:
        '''Get the inner text content of the target element.'''
        self.conn.send({'method': 'get_text'})
        return self.wait_for()

    def is_displayed(self) -> None:
        self.conn.send({'method': 'is_displayed'})
        return self.wait_for()

    def click(self) -> None:
        self.conn.send({'method': 'click'})
        return self.wait_for()

    def send_keys(self, keys: str) -> None:
        self.conn.send({'method': 'send_keys', 'keys': keys})
        return self.wait_for()


class UITest(TestCase):
    '''Base class for testing UI on browser. This class starts up an HTTP
    server on a new subprocess.

    Subclasses must override ``get_app()`` method, which returns the
    ``pygmariot.server.Application`` or ``tornado.web.Application`` to be
    tested.
    '''
    def setUp(self):
        self.wd = get_browser()
        self.loop = asyncio.get_event_loop()

        def start_server(app, port):
            server = HTTPServer(app)
            server.listen(port)
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

    def get_app(self) -> Application:
        '''This method should be overridden. Return
        ``pygmariot.server.Application`` or ``tornado.web.Application`` to be
        tested.
        '''
        NotImplementedError

    def wait(self, timeout=0.0):
        '''Wait until ``timeout``. The default timeout is zero, so wait a
        single event loop.'''
        self.loop.run_until_complete(asyncio.sleep(timeout))

    def send_keys(self, element, keys: str):
        '''Send ``keys`` to ``element`` one-by-one. Safer than using
        ``element.send_keys`` method.
        '''
        for k in keys:
            element.send_keys(k)
