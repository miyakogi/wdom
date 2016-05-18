import asyncio
from wdom.document import get_document
from wdom.server import start_server, stop_server
from wdom.tag import Button

if __name__ == '__main__':
    document = get_document()
    # Add <link>-tag sourcing bootstrap.min.css on <head>
    document.add_cssfile('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css')
    # Add <script>-tag sourcing jquery and bootstrap.min.js to <body>
    document.add_jsfile('https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js')
    document.add_jsfile('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js')

    # Add bootstrap button element
    document.body.appendChild(Button('click', class_='btn btn-primary'))

    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
