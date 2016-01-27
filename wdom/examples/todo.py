#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import Node
from wdom.view import get_document


class App(Node):
    tag = 'wdom-app'


class H1(Node):
    tag = 'h1'


class Input(Node):
    tag = 'input'


class Button(Node):
    tag = 'button'

class Div(Node):
    tag = 'div'


class Item(Node):
    tag = 'span'
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def sample_page() -> Node:
    app = App()
    title = H1(parent=app)
    title.textContent = 'Todo example'
    textbox = Input(parent=app)
    textbox.setAttribute('type', 'text')
    add_button = Button(parent=app)
    add_button.textContent = 'ADD'
    todo_list = Div(parent=app)
    todo_heading = Div(parent=todo_list)
    todo_heading.appendChild('Todo list')
    # add_button.addEventListener('click')

    def new_item(data=None) -> Node:
        item = Item()
        item.appendChild('New Item')
        todo_list.appendChild(item)
        return item

    # textbox.addEventListener('input', update)
    add_button.addEventListener('click', new_item)

    page = get_document(app=app)

    return page
