#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import webbrowser

from tornado import web
from tornado import websocket
from tornado.httpserver import HTTPServer

from wdom import options
from wdom.misc import static_dir

logger = logging.getLogger(__name__)


class MainHandler(web.RequestHandler):
    '''This is a main handler, which renders ``document`` object of the
    application. Must be used with an Application object which has ``document``
    attribute.'''
    def get(self):
        logger.info('connected')
        self.write(self.application.document.build())


class WSHandler(websocket.WebSocketHandler):
    def open(self):
        logger.info('WS OPEN')
        self.doc = self.application.document
        self.doc.connections.append(self)

    def on_message(self, message):
        # Log handling
        msg = json.loads(message)
        _type = msg.get('type')
        if _type == 'log':
            self.log_handler(msg.get('level'), msg.get('message'))
        elif _type in ('event', 'response'):
            self.element_handler(msg)

    def on_close(self):
        logger.info('RootWS CLOSED')
        if self in self.doc.connections:
            self.doc.connections.remove(self)

    def log_handler(self, level: str, message: str):
        message = 'JS: ' + str(message)
        if level == 'error':
            logger.error(message)
        elif level.startswith('warn'):
            logger.warning(message)
        elif level == 'info':
            logger.info(message)
        elif level == 'debug':
            logger.debug(message)

    def element_handler(self, msg: dict):
        id = msg.get('id')
        elm = self.doc.getElementById(id)
        if elm is not None:
            elm.on_message(msg)
        else:
            logger.warn('No such element: id={}'.format(id))


class Application(web.Application):
    '''A collection of settings required for a web server, including handlers,
    logging, and document object. This class is based on
    tornado.web.Application, but including some utility methods to make it
    easy to set up app.
    '''

    def __init__(self, *args, document=None, **kwargs):
        super().__init__(*args, **kwargs)
        if document is None:
            raise TypeError('Application requires "document" argument.')
        self.document = document

    def log_request(self, handler):
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
        '''Add path to serve static files. ``prefix`` is used for url prefix to
        serve static files and ``path`` is a path to the static file directory.
        ``prefix = '/_static'`` is reserved for the server, so do not use it
        for your app.
        '''
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
        '''Add path to the directory, which contains favicon file
        (``favicon.ico``) for your app.
        '''
        spec = web.URLSpec(
            '/(favicon.ico)',
            web.StaticFileHandler,
            dict(path=path)
        )
        # Need some check
        handlers = self.handlers[0][1]
        handlers.append(spec)


def get_app(document, debug=None, **kwargs) -> Application:
    '''Return Application object to serve ``document``.'''
    if debug is None:
        if 'debug' not in options.config:
            options.parse_command_line()
        debug = options.config.debug
    app = Application(
        [(r'/', MainHandler),
         (r'/rimo_ws', WSHandler),
         ],
        document=document,
        debug=debug,
        **kwargs
    )

    # Add application's static files directory
    app.add_static_path('_static', static_dir)
    return app


def start_server(app: web.Application, port=None, browser=None, **kwargs) -> HTTPServer:
    '''Start server with ``app`` on ``localhost:port``.
    If port is not specified, use command line option of ``--port``.

    If ``browser`` is not specified, do not open the page. When ``browser`` is
    specified, open the page with the specified browser. The specified browser
    name is not registered in ``webbrowser`` module, or, for example it is just
    ``True``, use system's default browser to open the page.
    '''
    if port is None:
        if 'port' not in options.config:
            options.parse_command_line()
        port = options.config.port
    logger.info('Start server on port {0:d}'.format(port))
    server = app.listen(port)

    if browser is not None:
        url = 'http://localhost:{}/'.format(port)
        if browser in webbrowser._browsers:
            webbrowser.get(browser).open(url)
        else:
            webbrowser.open(url)

    return server

def stop_server(server):
    server.stop()
    logger.info('Server terminated')
