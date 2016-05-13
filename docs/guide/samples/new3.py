#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from wdom.server import start_server, stop_server
from wdom.document import get_document
from wdom.tag import Button, Div


class MyButton(Button):
    # tag = 'button'  <- tag name is already defined in Button class
    class_ = 'btn'
    is_ = 'my-button'  # set name at is_


class DefaultButton(MyButton):
    class_ = 'btn-default'
    is_ = 'default-button'


if __name__ == '__main__':
    document = get_document()
    # Register MyElement
    document.defaultView.customElements.define('my-button', MyButton, {'extends': 'button'})
    document.defaultView.customElements.define('default-button', DefaultButton, {'extends': 'button'})

    # Load css and js file for bootstrap
    document.add_cssfile('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css')
    document.add_jsfile('https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js')
    document.add_jsfile('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js')

    div = Div(parent=document.body)
    div.innerHTML = '''
        <button is="my-button">MyButton</button>
        <button is="default-button">DefaultButton</button>
    '''.strip()
    print(isinstance(div.firstChild, MyButton))  # True
    print(isinstance(div.lastChild, DefaultButton))  # True

    start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_server()
