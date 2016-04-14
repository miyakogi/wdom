#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom import tag
from wdom.document import Document, get_document


def sample_app(theme=tag) -> tag.Tag:
    app = theme.Div(class_='container')
    content_wrapper = theme.Div()
    content_wrapper['style'] = '''\
        margin-top: 2em;
        margin-bottom: 2em;
        margin-left: 2em;
        margin-right: 2em;
    '''
    app.append(content_wrapper)
    body = content_wrapper

    button_wrapper = theme.Div(parent=body)
    button_wrapper.append(theme.DefaultButton('Default'))
    button_wrapper.append(theme.PrimaryButton('Primary'))
    button_wrapper.append(theme.SuccessButton('Success'))
    button_wrapper.append(theme.InfoButton('Info'))
    button_wrapper.append(theme.WarningButton('Warning'))
    button_wrapper.append(theme.DangerButton('Danger'))
    button_wrapper.append(theme.LinkButton('Link'))

    input_wrapper = theme.FormGroup(parent=body)
    input_wrapper.append(theme.Textarea())
    input_wrapper.append(theme.Input())

    dropdown_list = theme.Select(parent=body)
    dropdown_list.append(theme.Option('Item 1'))
    dropdown_list.append(theme.Option('Item 2'))
    dropdown_list.append(theme.Option('Item 3'))

    return app


def sample_page(theme=tag) -> Document:
    page = get_document()
    app = sample_app(theme)
    page.body.prepend(app)
    for css in theme.css_files:
        page.add_cssfile(css)
    for js in theme.js_files:
        page.add_jsfile(js)
    return page
