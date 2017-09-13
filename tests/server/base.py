#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
import time

from tornado.httpclient import AsyncHTTPClient, HTTPResponse
from tornado.platform.asyncio import to_asyncio_future
from tornado.websocket import websocket_connect, WebSocketClientConnection

from wdom import server

from ..base import TestCase

logger = logging.getLogger(__name__)
root_logger = logging.getLogger('wdom')
server_config = server.server_config


class HTTPTestCase(TestCase):
    """For http/ws connection test."""

    wait_time = 0.05 if os.getenv('TRAVIS') else 0.01
    timeout = 1.0
    _server_started = False
    _ws_connections = []

    def start(self) -> None:
        """Start web server.

        Please call this method after prepraring document.
        """
        time.sleep(0.1)
        with self.assertLogs(root_logger, 'INFO'):
            self.server = server.start_server(port=0)
        time.sleep(0.1)
        self.port = server_config['port']
        self.url = 'http://localhost:{}'.format(self.port)
        self.ws_url = 'ws://localhost:{}'.format(self.port)
        self._server_started = True

    def tearDown(self) -> None:
        """Terminate server and close all ws client connections."""
        if self._server_started:
            with self.assertLogs(root_logger, 'INFO'):
                server.stop_server(self.server)
            self._server_started = False
        while self._ws_connections:
            ws = self._ws_connections.pop()
            ws.close()
        super().tearDown()

    async def fetch(self, url: str, encoding: str = 'utf-8') -> HTTPResponse:
        """Fetch url and return ``tornado.httpclient.HTTPResponse`` object.

        Response body is decoded by ``encoding`` and set ``text`` property of
        the response. If failed to decode, ``text`` property will be ``None``.
        """
        response = await to_asyncio_future(
            AsyncHTTPClient().fetch(url, raise_error=False))
        if response.body:
            try:
                response.text = response.body.decode(encoding)
            except UnicodeDecodeError:
                response.text = None
        else:
            response.text = None
        return response

    async def ws_connect(self, url: str, timeout: float = None
                         ) -> WebSocketClientConnection:
        """Make WebSocket connection to the url.

        Retries up to _max (default: 20) times. Client connections made by this
        method are closed after each test method.
        """
        st = time.perf_counter()
        timeout = timeout or self.timeout
        while (time.perf_counter() - st) < timeout:
            try:
                ws = await to_asyncio_future(websocket_connect(url))
            except ConnectionRefusedError:
                await self.wait()
                continue
            else:
                self._ws_connections.append(ws)
                return ws
        raise ConnectionRefusedError(
            'WebSocket connection refused: {}'.format(url))

    async def wait(self, timeout: float = None, times: int = 1) -> None:
        """Coroutine to wait for ``timeout``.

        ``timeout`` is second to wait, and its default value is
        ``self.wait_time``. If ``times`` are specified, wait for
        ``timeout * times``.
        """
        for i in range(times):
            await asyncio.sleep(timeout or self.wait_time)
