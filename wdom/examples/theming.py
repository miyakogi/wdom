#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom import tag
from wdom.document import Document, get_document


def sample_app(theme=tag) -> tag.Tag:
    app = theme.Container()
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
    button_wrapper.append(
        theme.DefaultButton('Default'),
        theme.PrimaryButton('Primary'),
        theme.SuccessButton('Success'),
        theme.InfoButton('Info'),
        theme.WarningButton('Warning'),
        theme.DangerButton('Danger'),
        theme.LinkButton('Link'),
    )

    input_wrapper = theme.FormGroup(parent=body)
    input_wrapper.append(theme.Textarea())
    input_wrapper.append(theme.Input())

    dropdown_list = theme.Select(parent=body)
    dropdown_list.append(
        theme.Option('Item 1'),
        theme.Option('Item 2'),
        theme.Option('Item 3'),
    )

    # List
    list_div = theme.Div(parent=body)
    ul1 = theme.Ul(parent=list_div)
    ul1.append(theme.Li('Item 1'))
    li = theme.Li('Item 2', parent=ul1)
    ul2 = theme.Ul(parent=li)
    ul2.append(
        theme.Li('Item 2.1'),
        theme.Li('Item 2.2'),
        theme.Li('Item 3'),
    )

    code_div = theme.Div(parent=body)
    pre = theme.Pre(parent=code_div)
    pre.append(theme.Code(
        '''\
    def python(i: int) -> str:
        print(str(i))
    '''.rstrip()))

    # Table
    table_div = theme.Div(parent=body)
    table = theme.Table(parent=table_div)

    thead = theme.Th(parent=table)
    tr1 = theme.Tr(parent=thead)
    tr1.append(
        theme.Th('Name'),
        theme.Th('Age'),
        theme.Th('Seibetsu'),
        theme.Th('Location'),
    )

    tbody = theme.Tbody(parent=table)
    tr2 = theme.Tr(parent=tbody)
    tr2.append(
        theme.Td('Ichiro Suzuki'),
        theme.Td('26'),
        theme.Td('Male'),
        theme.Td('Tokyo'),
    )

    tr3 = theme.Tr(parent=tbody)
    tr3.append(
        theme.Td('Hikari Takiguchi'),
        theme.Td('20'),
        theme.Td('Female'),
        theme.Td('Kyoto'),
    )

    # Typography
    typography = theme.Div(parent=body)
    typography.append(
        theme.H1('Heading 1'),
        theme.H2('Heading 2'),
        theme.H3('Heading 3'),
        theme.H4('Heading 4'),
        theme.H5('Heading 5'),
        theme.H6('Heading 6'),
        theme.P('This is the base paragraph.'),
        theme.Strong('Bolded'),
        theme.Em('Italicized'),
        theme.A('Colored (link)'),
        theme.U('Underlined'),
    )

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
