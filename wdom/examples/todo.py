#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import Tag
from wdom.document import get_document


class App(Tag):
    tag = 'wdom-app'


class H1(Tag):
    tag = 'h1'


class Input(Tag):
    tag = 'input'


class Button(Tag):
    tag = 'button'

class Div(Tag):
    tag = 'div'


class Item(Tag):
    tag = 'span'
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def sample_page() -> Tag:
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

    def new_item(event=None) -> Tag:
        item = Item()
        item.appendChild('New Item')
        todo_list.appendChild(item)
        return item

    # textbox.addEventListener('input', update)
    add_button.addEventListener('click', new_item)

    page = get_document(app=app)

    return page
