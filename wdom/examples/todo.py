#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.themes.bootstrap3 import Tag, H1, Input, Button, Div
from wdom.document import get_document, Document


class App(Div):
    pass


class Item(Tag):
    tag = 'span'
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def sample_page(**kwargs) -> Document:
    app = App()
    title = H1(parent=app)
    title.textContent = 'Todo example'
    textbox = Input(parent=app)
    textbox.setAttribute('type', 'text')
    add_button = Button(parent=app)
    add_button.textContent = 'ADD'
    todo_list = Div(parent=app)
    todo_heading = Div(parent=todo_list)
    todo_heading.append('Todo list')
    # add_button.addEventListener('click')

    def new_item(event=None) -> Tag:
        item = Item()
        item.append('New Item')
        todo_list.append(item)
        return item

    # textbox.addEventListener('input', update)
    add_button.addEventListener('click', new_item)

    page = get_document(app=app, **kwargs)

    return page
