#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import socket
from typing import Optional

from tornado import web
from tornado import websocket
from tornado.httpserver import HTTPServer

from wdom.options import config
from wdom.misc import install_asyncio
from wdom.server.handler import on_websocket_message

logger = logging.getLogger(__name__)
install_asyncio()
connections = []


def is_connected():
    """Check if tornado web server has a client connection."""
    return any(connections)


class MainHandler(web.RequestHandler):
    """Main handler to serve document of the application."""
    def get(self):
        """Return whole html representation of the root document."""
        from wdom.document import get_document
        logger.info('connected')
        self.write(get_document().build())


class WSHandler(websocket.WebSocketHandler):
    """Handler class of web socket connection."""
    def open(self):
        """Called when connection open."""
        logger.info('WS OPEN')
        connections.append(self)

    def on_message(self, message):
        """Called when get message from client."""
        on_websocket_message(message)

    @asyncio.coroutine
    def terminate(self):
        """Terminate server if no more connection exists."""
        yield from asyncio.sleep(config.shutdown_wait)
        # stop server and close loop if no more connection exists
        if not is_connected():
            stop_server(self.application.server)
            self.application.server.io_loop.stop()

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
    """Application for a tornado web server.

    This class is based on tornado.web.Application, but including some utility
    methods to make it easy to set up app.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            [(r'/', MainHandler), (r'/rimo_ws', WSHandler)],
            *args,
            debug=config.debug,
            autoreload=False,
            static_hash_cashe=False,
            compiled_template_cashe=False,
            **kwargs
        )

    def log_request(self, handler):
        """Handle access log."""
        if 'log_function' in self.settings:
            self.settings['log_function'](handler)
            return
        status = handler.get_status()
        if status < 400:
            log_method = logger.info
        elif status < 500:
            log_method = logger.warning
        else:
            log_method = logger.error
        request_time = 1000.0 * handler.request.request_time()
        if request_time > 10:
            logger.warning('%d %s %.2fms',
                           status, handler._request_summary(), request_time)
        else:
            log_method('%d %s', status, handler._request_summary())

    def add_static_path(self, prefix: str, path: str):
        """Add path to serve static files.

        ``prefix`` is used for url prefix to serve static files and ``path`` is
        a path to the static file directory. ``prefix = '/_static'`` is
        reserved for the server, so do not use it for your app.
        """
        pattern = prefix
        if not pattern.startswith('/'):
            pattern = '/' + pattern
        if not pattern.endswith('/(.*)'):
            pattern = pattern + '/(.*)'
        spec = web.URLSpec(pattern, web.StaticFileHandler, dict(path=path))
        # Need some check
        handlers = self.handlers[0][1]
        handlers.append(spec)

    def add_favicon_path(self, path: str):
        """Add path to serve favicon file.

        ``path`` should be a directory, which contains favicon file
        (``favicon.ico``) for your app.
        """
        spec = web.URLSpec(
            '/(favicon.ico)',
            web.StaticFileHandler,
            dict(path=path)
        )
        # Need some check
        handlers = self.handlers[0][1]
        handlers.append(spec)


main_application = Application()


def get_app(*args, **kwargs) -> Application:
    """Return Application object to serve ``document``."""
    return main_application


def set_application(app: Application):
    """Set application as a root application for the server."""
    global main_application
    main_application = app


def start_server(app: web.Application = None, port: int = None,
                 browser: str = None, address: str = None,
                 check_time: Optional[int] = 500,
                 **kwargs) -> HTTPServer:
    """Start server with ``app`` on ``localhost:port``.

    If port is not specified, use command line option of ``--port``.

    If ``browser`` is not specified, do not open the page. When ``browser`` is
    specified, open the page with the specified browser. The specified browser
    name is not registered in ``webbrowser`` module, or, for example it is just
    ``True``, use system's default browser to open the page.
    """
    app = app or get_app()
    port = port if port is not None else config.port
    address = address if address is not None else config.address

    server = app.listen(port, address=address)
    app.server = server
    server.address = address
    for sock in server._sockets.values():
        if sock.family == socket.AF_INET:
            server.port = sock.getsockname()[1]
            break
    return server


def stop_server(server: HTTPServer):
    """Terminate given server."""
    server.stop()
    logger.info('Server terminated')
