import asyncio
from wdom.document import get_document
from wdom.server import start_server, stop_server
from wdom.tag import Link, Script, Button

if __name__ == '__main__':
    document = get_document()
    # Add <link>-tag sourcing bootstrap.min.css on <head>
    document.head.appendChild(Link(rel='stylesheet', href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css'))

    # Add <script>-tag sourcing jquery and bootstrap.min.js to <body>
    document.body.appendChild(Script(src='https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js'))
    document.body.appendChild(Script(src='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js'))

    # Add bootstrap button element
    document.body.appendChild(Button('click', class_='btn btn-primary'))

    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
