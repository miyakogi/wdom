#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import socket
from typing import Optional

from aiohttp import web, MsgType

from wdom.options import config
from wdom.server.handler import on_websocket_message

logger = logging.getLogger(__name__)
connections = []
_access_log_format = '%s %r (%a) %D us'


def is_connected():
    """Check if aiohttp server has a client connection."""
    return any(connections)


def main_handler(request):
    """Main handler to serve root ``document`` object of the application."""
    from wdom.document import get_document
    logger.info('connected')
    return web.Response(body=get_document().build().encode())


@asyncio.coroutine
def ws_open(request):
    """Open websocket connection of aiohttp."""
    handler = WSHandler()
    logger.info('WS OPEN')
    yield from handler.open(request)
    return handler.ws


class WSHandler:
    """Wrapper class for aiohttp websockets.

    APIs are similar to ``tornaod.websocket.WebSocketHandler``.
    """
    @asyncio.coroutine
    def open(self, request):
        """Open new websocket connection and keep it."""
        self.req = request
        self.ws = web.WebSocketResponse()
        yield from self.ws.prepare(request)
        connections.append(self)

        while not self.ws.closed:
            msg = yield from self.ws.receive()
            if msg.tp == MsgType.text:
                yield from self.on_message(msg.data)
            elif msg.tp in (MsgType.close, MsgType.closed, MsgType.error):
                yield from self.ws.close()
        self.on_close()
        return self.ws

    def write_message(self, message):
        """Send message to the client."""
        self.ws.send_str(message)

    @asyncio.coroutine
    def on_message(self, message):
        """Called when get message from client."""
        on_websocket_message(message)

    @asyncio.coroutine
    def terminate(self):
        """Terminate if no more connection."""
        yield from asyncio.sleep(config.shutdown_wait)
        # stop server and close loop if no more connection exists
        if not is_connected():
            server = self.req.app['server']
            yield from terminate_server(server)
            server._loop.stop()

    def on_close(self):
        """Called when connection closed."""
        logger.info('RootWS CLOSED')
        if self in connections:
            # Remove this connection from connection-list
            connections.remove(self)
        # close if auto_shutdown is enabled and there is no more connection
        if config.auto_shutdown and not is_connected():
            asyncio.ensure_future(self.terminate())


class Application(web.Application):
    """Web server application class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.router.add_route('GET', '/', MainHandler)
        root_resource = self.router.add_resource('/', name='root')
        root_resource.add_route('GET', main_handler)
        # self.router.add_route('*', '/rimo_ws', ws_open)
        root_ws_resource = self.router.add_resource('/rimo_ws', name='root_ws')
        root_ws_resource.add_route('*', ws_open)

    def add_static_path(self, prefix: str, path: str):
        """Add directory to serve static files."""
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        self.router.add_static(prefix, path)

    def add_favicon_path(self, path: str):
        """Add path to serve favicon file."""
        self.router.add_static('/(favicon.ico)', path)


main_application = Application()


def get_app(*args, **kwargs) -> web.Application:
    """Make Application object to serve ``document``."""
    return main_application


def set_application(app: Application):
    """Set application as a root application."""
    global main_application
    main_application = app


@asyncio.coroutine
def close_connections(app: web.Application):
    """Close all websocket connections."""
    for conn in connections:
        yield from conn.ws.close(code=999, message='server shutdown')


def start_server(app: Optional[web.Application] = None,
                 port: Optional[int] = None,
                 browser: Optional[str] = None,
                 loop: Optional[asyncio.BaseEventLoop] = None,
                 address: Optional[str] = None,
                 family: Optional[socket.AddressFamily] = socket.AF_INET,
                 check_time: Optional[int] = 500,
                 ) -> asyncio.base_events.Server:
    """Start server with ``app`` on ``address:port``.

    If port is not specified, use command line option of ``--port``.

    When ``browser`` is specified, open the page with the specified browser.
    The specified browser name is not registered in ``webbrowser`` module, or,
    for example it is just ``True``, use system's default browser to open the
    page.
    """
    port = port if port is not None else config.port
    address = address if address is not None else config.address
    app = app or get_app()
    loop = loop or asyncio.get_event_loop()

    handler = app.make_handler(logger=logger, access_log=logger,
                               access_log_format=_access_log_format)
    f = loop.create_server(handler, address, port)
    server = loop.run_until_complete(f)
    server.app = app
    server.handler = handler
    server.port = server.sockets[-1].getsockname()[1]
    server.address = address or 'localhost'
    app.on_shutdown.append(close_connections)
    app['server'] = server

    return server


@asyncio.coroutine
def terminate_server(server: asyncio.base_events.Server):
    """Close all connections and terminate server."""
    logger.info('Start server shutdown')
    server.close()
    yield from server.wait_closed()
    yield from server.app.shutdown()
    yield from server.handler.finish_connections(1.0)
    yield from server.app.cleanup()
    logger.info('Server terminated')


def stop_server(server: asyncio.base_events.Server):
    """Terminate given server."""
    server._loop.run_until_complete(terminate_server(server))
