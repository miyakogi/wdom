#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import asyncio
import socket
from typing import Optional

from aiohttp import web, MsgType
from tornado import autoreload

from wdom.options import config
from wdom.misc import static_dir
from wdom.handler import event_handler, log_handler, response_handler
from wdom.document import get_document
from wdom.server_base import open_browser, watch_dir

logger = logging.getLogger(__name__)


class MainHandler(web.View):
    '''This is a main handler, which renders ``document`` object of the
    application. Must be used with an Application object which has ``document``
    attribute.'''
    async def get(self):
        logger.info('connected')
        return web.Response(body=get_document().build().encode())


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
        get_document().connections.append(self)

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
            event_handler(msg, get_document())
        elif _type == 'response':
            response_handler(msg, get_document())
        else:
            raise ValueError('unkown message type: {}'.format(message))

    async def terminate(self):
        await asyncio.sleep(config.shutdown_wait)
        if not any(get_document().connections):
            server = self.req.app['server']
            await terminate_server(server)
            server._loop.stop()

    def on_close(self):
        doc = get_document()
        logger.info('RootWS CLOSED')
        if self in doc.connections:
            doc.connections.remove(self)
        if config.auto_shutdown and not any(doc.connections):
            asyncio.ensure_future(self.terminate())


class Application(web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router.add_route('GET', '/', MainHandler)
        self.router.add_route('*', '/rimo_ws', ws_open)

    def add_static_path(self, prefix: str, path: str, no_watch: bool = False):
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        self.router.add_static(prefix, path)
        if not no_watch:
            watch_dir(path)

    def add_favicon_path(self, path: str):
        self.router.add_static('/(favicon.ico)', path)


main_application = Application()


def get_app(*args, **kwargs) -> web.Application:
    '''Make Application object to serve ``document``.'''
    return main_application


def set_application(app:Application):
    global main_application
    main_application = app

async def close_connections(app: web.Application):
    for conn in get_document().connections:
        await conn.ws.close(code=999, message='server shutdown')


def start_server(app: Optional[web.Application] = None,
                 port: Optional[int] = None,
                 browser: Optional[str] = None,
                 loop: Optional[asyncio.BaseEventLoop] = None,
                 address: Optional[str] = None,
                 family: Optional[socket.AddressFamily] = socket.AF_INET,
                 check_time: Optional[int] = 500,
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

    # Add application's static files directory
    if app is None:
        app = get_app()
    app.add_static_path('_static', static_dir)
    doc = get_document()
    if os.path.exists(doc.tempdir):
        print('add tempdir')
        app.add_static_path('tmp', doc.tempdir, no_watch=True)

    loop = loop or asyncio.get_event_loop()
    logger.info('Start server on {0}:{1:d}'.format(address, port))
    handler = app.make_handler()
    f = loop.create_server(handler, address, port)
    server = loop.run_until_complete(f)
    server.app = app
    server.handler = handler
    app.on_shutdown.append(close_connections)
    app['server'] = server
    if doc._autoreload:
        from wdom.misc import install_asyncio
        install_asyncio()
        autoreload.start(check_time=check_time)

    if config.open_browser:
        open_browser('http://{}:{}/'.format(address, port), browser)

    return server


async def terminate_server(server: asyncio.base_events.Server):
    logger.info('Start server shutdown')
    server.close()
    await server.wait_closed()
    await server.app.shutdown()
    await server.handler.finish_connections(1.0)
    await server.app.cleanup()
    logger.info('Server terminated')


def stop_server(server: asyncio.base_events.Server):
    '''Terminate given server.'''
    server._loop.run_until_complete(terminate_server(server))
