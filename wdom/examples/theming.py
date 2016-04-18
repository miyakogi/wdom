#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from wdom import themes, options, tag
from wdom.document import Document, get_document


def _get_theme_name(theme) -> str:
    if theme.__name__ == 'wdom.themes':
        if options.config.theme:
            theme_name = options.config.theme.upper()
        else:
            theme_name = 'DEFAULT'
    else:
        theme_name = re.search(r'.*\.(.*?)$', theme.__name__).group(1).upper()
    return theme_name

def sample_app(theme=themes) -> tag.Tag:
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
    body.append(theme.Div(theme.H1(_get_theme_name(theme)),
                          style='text-align: center;'))
    body.append(theme.Hr())

    button_wrapper = theme.Div(parent=body)
    button_wrapper.append(
        theme.Button('Button'),
        theme.DefaultButton('Default'),
        theme.PrimaryButton('Primary'),
        theme.SuccessButton('Success'),
        theme.InfoButton('Info'),
        theme.WarningButton('Warning'),
        theme.DangerButton('Danger'),
        theme.LinkButton('Link'),
    )
    body.append(theme.Hr())

    input_wrapper = theme.Form(parent=theme.FormGroup(parent=body))
    input_wrapper.append(
        theme.Textarea(),
        theme.Input(),
    )

    dropdown_list = theme.Select(parent=body)
    dropdown_list.append(
        theme.Option('Item 1'),
        theme.Option('Item 2'),
        theme.Option('Item 3'),
    )
    body.append(theme.Hr())

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
    body.append(theme.Hr())

    code_div = theme.Div(parent=body)
    pre = theme.Pre(parent=code_div)
    pre.append(theme.Code(
        '''\
    def python(i: int) -> str:
        print(str(i))
    '''.rstrip()))
    body.append(theme.Hr())

    # Table
    table_div = theme.Div(parent=body)
    table = theme.Table(parent=table_div)

    thead = theme.Thead(parent=table)
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
    body.append(theme.Hr())

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
        theme.Div(theme.Em('Italicized')),
        theme.Div(theme.A('Colored (link)')),
        theme.Div(theme.U('Underlined')),
    )
    body.append(theme.Hr())

    grid = theme.Container(parent=body)
    left_style = 'background-color: #333; color: #eee'
    right_style = 'background-color: #ccc'
    for i in range(0, 13):
        l = 'Col' + str(i or '')
        r = 'Col' + str(12 - i or '')
        grid.append(theme.Row(
            getattr(theme, l)(l, style=left_style),
            getattr(theme, r)(r, style=right_style),
        ))

    return app


def sample_page(theme=themes) -> Document:
    page = get_document()
    app = sample_app(theme)
    page.body.prepend(app)
    for css in theme.css_files:
        page.add_cssfile(css)
    for js in theme.js_files:
        page.add_jsfile(js)
    return page
