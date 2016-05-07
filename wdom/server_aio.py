#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import asyncio
import socket

from aiohttp import web, MsgType
from tornado import autoreload

from wdom.options import config
from wdom.misc import static_dir
from wdom.handler import event_handler, log_handler, response_handler
from wdom.document import Document
from wdom.server_base import open_browser, watch_dir

logger = logging.getLogger(__name__)


class MainHandler(web.View):
    '''This is a main handler, which renders ``document`` object of the
    application. Must be used with an Application object which has ``document``
    attribute.'''
    async def get(self):
        logger.info('connected')
        return web.Response(body=self.request.app['document'].build().encode())


async def ws_open(request):
    '''Open websocket for aiohttp.'''
    handler = WSHandler()
    await handler.open(request)
    return handler.ws


class WSHandler:
    '''Wrapper class for aiohttp websockets. APIs are similar to
    ``tornaod.websocket.WebSocketHandler``.
    '''
    async def open(self, request):
        self.req = request
        self.ws = web.WebSocketResponse()
        await self.ws.prepare(request)
        self.doc = self.req.app['document']
        self.doc.connections.append(self)

        while not self.ws.closed:
            msg = await self.ws.receive()
            if msg.tp == MsgType.text:
                await self.on_message(msg.data)
            elif msg.tp in (MsgType.close, MsgType.closed, MsgType.error):
                await self.ws.close()
        self.on_close()
        return self.ws

    def write_message(self, message):
        self.ws.send_str(message)

    async def on_message(self, message):
        msg = json.loads(message)
        _type = msg.get('type')
        if _type == 'log':
            log_handler(msg.get('level'), msg.get('message'))
        elif _type == 'event':
            event_handler(msg, self.doc)
        elif _type == 'response':
            response_handler(msg, self.doc)
        else:
            raise ValueError('unkown message type: {}'.format(message))

    async def terminate(self):
        await asyncio.sleep(config.shutdown_wait)
        if not any(self.doc.connections):
            server = self.req.app['server']
            await terminate_server(server)
            server._loop.stop()

    def on_close(self):
        logger.info('RootWS CLOSED')
        if self in self.doc.connections:
            self.doc.connections.remove(self)
        if config.auto_shutdown and not any(self.doc.connections):
            asyncio.ensure_future(self.terminate())


class Application(web.Application):
    def add_static_path(self, prefix:str, path:str, no_watch: bool = False):
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        self.router.add_static(prefix, path)
        if not no_watch:
            watch_dir(path)

    def add_favicon_path(self, path:str):
        self.router.add_static('/(favicon.ico)', path)


def get_app(document:Document, debug=None, **kwargs) -> web.Application:
    '''Make Application object to serve ``document``.'''
    if debug is None:
        debug = config.debug

    app = Application()
    app.router.add_route('GET', '/', MainHandler)
    app.router.add_route('*', '/rimo_ws', ws_open)
    app['document'] = document

    # Add application's static files directory
    app.add_static_path('_static', static_dir)
    if os.path.exists(document.tempdir):
        app.add_static_path('tmp', document.tempdir, no_watch=True)
    return app


async def close_connections(app:web.Application):
    for conn in app['document'].connections:
        await conn.ws.close(code=999, message='server shutdown')


def start_server(app: web.Application, port=None, browser=None, loop=None,
                 address=None, family=socket.AF_INET, check_time=500,
                 ) -> asyncio.base_events.Server:
    '''Start server with ``app`` on ``address:port``.
    If port is not specified, use command line option of ``--port``.

    When ``browser`` is specified, open the page with the specified browser.
    The specified browser name is not registered in ``webbrowser`` module, or,
    for example it is just ``True``, use system's default browser to open the
    page.
    '''
    port = port if port is not None else config.port
    address = address if address is not None else config.address

    loop = loop or asyncio.get_event_loop()
    logger.info('Start server on {0}:{1:d}'.format(address, port))
    handler = app.make_handler()
    f = loop.create_server(handler, address, port)
    server = loop.run_until_complete(f)
    server.app = app
    server.handler = handler
    app.on_shutdown.append(close_connections)
    app['server'] = server
    if app['document']._autoreload:
        from wdom.misc import install_asyncio
        install_asyncio()
        autoreload.start(check_time=check_time)

    if config.open_browser:
        open_browser('http://{}:{}/'.format(address, port), browser)

    return server


async def terminate_server(server:asyncio.base_events.Server):
    logger.info('Start server shutdown')
    server.close()
    await server.wait_closed()
    await server.app.shutdown()
    await server.handler.finish_connections(1.0)
    await server.app.cleanup()
    logger.info('Server terminated')


def stop_server(server:asyncio.base_events.Server):
    '''Terminate given server.'''
    server._loop.run_until_complete(terminate_server(server))
