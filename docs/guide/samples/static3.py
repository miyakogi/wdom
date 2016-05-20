import asyncio
from os import path

from wdom.document import get_document
from wdom.server import start_server, stop_server, add_static_path
from wdom.tag import Button

if __name__ == '__main__':
    static_dir = path.join(path.dirname(path.abspath(__file__)), 'static')
    document = get_document()
    document.add_cssfile('/static/css/app.css')

    # Add button element
    document.body.appendChild(Button('click'))

    add_static_path('static', static_dir)
    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
