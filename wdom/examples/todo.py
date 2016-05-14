#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.themes.bootstrap3 import Tag, H1, Button, Div
from wdom.themes.bootstrap3 import Container, FormGroup, TextInput
from wdom.themes.bootstrap3 import css_files, js_files
from wdom.document import get_document, Document


class Item(Tag):
    tag = 'span'
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def sample_page(**kwargs) -> Document:
    app = Container()
    title = H1(parent=app)
    title.textContent = 'Todo example'
    form = FormGroup(parent=app)
    text_input = TextInput()
    form.append(text_input)
    add_button = Button(parent=form)
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

    add_button.addEventListener('click', new_item)

    page = get_document(app=app, **kwargs)
    for css in css_files:
        page.add_cssfile(css)
    for js in js_files:
        page.add_jsfile(js)

    return page
