#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.themes.bootstrap3 import Tag, Div, DefaultButton, PrimaryButton, DangerButton
from wdom.themes.bootstrap3 import FormGroup, TextArea, TextInput, Option, Select
from wdom.themes.bootstrap3 import js_files, css_files
from wdom.document import Document, get_document


def sample_app() -> Tag:
    app = Div(class_='container')
    content_wrapper = Div()
    content_wrapper['style'] = '''\
        margin-top: 2em;
        margin-bottom: 2em;
        margin-left: 2em;
        margin-right: 2em;
    '''
    app.append(content_wrapper)
    body = content_wrapper

    button_wrapper = Div()

    btn1 = DefaultButton()
    btn2 = PrimaryButton()
    btn3 = DangerButton()
    button_wrapper.append(btn1)
    button_wrapper.append(btn2)
    button_wrapper.append(btn3)
    btn1.textContent = 'default'
    btn2.textContent = 'primary'
    btn3.textContent = 'danger'

    input_wrapper = FormGroup()
    textarea = TextArea()
    textinput = TextInput()
    input_wrapper.append(textarea)
    input_wrapper.append(textinput)

    item1 = Option()
    item2 = Option()
    item3 = Option()
    item1.textContent = 'Item 1'
    item2.textContent = 'Item 2'
    item3.textContent = 'Item 3'
    dropdown_list = Select()
    dropdown_list.append(item1)
    dropdown_list.append(item2)
    dropdown_list.append(item3)

    body.append(button_wrapper)
    body.append(input_wrapper)
    body.append(dropdown_list)

    return app


def sample_page() -> Document:
    page = get_document()
    app = sample_app()
    page.body.prepend(app)
    for css in css_files:
        page.add_cssfile(css)
    for js in js_files:
        page.add_jsfile(js)
    return page
