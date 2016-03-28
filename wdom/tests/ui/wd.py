#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import asyncio
from multiprocessing import Process

from selenium import webdriver
from selenium.webdriver.common.utils import free_port

driver = webdriver.Firefox


def start_wd():
    if globals().get('wd') is None:
        global wd
        wd = driver()


def close_wd():
    if globals().get('wd') is not None:
        global wd
        wd.close()
        wd = None


def get_wd():
    if globals().get('wd') is None:
        start_wd()
    return wd


class UITest:
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
        self.wd = get_wd()
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
