#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from pathlib import Path

logger = logging.getLogger('wdom')
CURFILE = Path(__file__).resolve()
CURDIR = CURFILE.parent.resolve()

if __name__ == '__main__':
    sys.path.insert(0, str(CURDIR.parent.resolve()))


def main():
    # from tornado.ioloop import IOLoop
    # from tornado.platform.asyncio import AsyncIOMainLoop
    import asyncio
    from wdom.misc import install_asyncio
    install_asyncio()

    from wdom.server import start_server, get_app, stop_server
    # from wdom.server_aio import start_server, get_app, stop_server
    # from wdom.server_tornado import start_server, get_app, stop_server
    # from wdom.examples.markdown_simple import sample_page
    # from wdom.examples.rev_text import sample_page
    # from wdom.examples.data_binding import sample_page
    # from wdom.examples.todo import sample_page
    from wdom.examples.theming import sample_page
    # from wdom.themes import bootstrap3, mdl, skeleton, pure, semantic, kube, foundation, mui
    from wdom.themes import default
    page = sample_page(default)
    app = get_app(document=page)
    loop = asyncio.get_event_loop()
    server = start_server(app=app, loop=loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        stop_server(server)
        loop.close()


if __name__ == '__main__':
    main()
