#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from pathlib import Path

logger = logging.getLogger('wdom')
_CURFILE = Path(__file__).resolve()
_CURDIR = _CURFILE.parent.resolve()

if __name__ == '__main__':
    sys.path.insert(0, str(_CURDIR.parent.resolve()))


def main():
    from wdom.options import parse_command_line
    parse_command_line()
    from wdom.log import configure_logger
    configure_logger()

    # ADD js/css/template files for autoreload
    from tornado import autoreload
    for file_ in (_CURDIR.glob('_static/js/**/*.js')):
        autoreload.watch(str(file_))
    for file_ in (_CURDIR.glob('_static/css/*.css')):
        autoreload.watch(str(file_))
    for file_ in (_CURDIR.glob('_templates/*.html')):
        autoreload.watch(str(file_))

    # from tornado.ioloop import IOLoop
    from tornado.platform.asyncio import AsyncIOMainLoop
    import asyncio
    AsyncIOMainLoop().install()
    autoreload.start(check_time=200)

    from wdom.server import start_server, get_app, stop_server
    # from wdom.server_aio import start_server, get_app, stop_server
    # from wdom.server_tornado import start_server, get_app, stop_server
    # from wdom.examples.bootstrap3 import sample_page
    # from wdom.examples.markdown_simple import sample_page
    # from wdom.examples.rev_text import sample_page
    # from wdom.examples.data_binding import sample_page
    from wdom.examples.todo import sample_page
    page = sample_page()
    app = get_app(document=page)
    loop = asyncio.get_event_loop()
    server = start_server(app=app, loop=loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_server(server)
    loop.close()


if __name__ == '__main__':
    main()
