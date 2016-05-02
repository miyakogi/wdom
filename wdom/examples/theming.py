#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
from pathlib import Path

CURFILE = Path(__file__).resolve()
CURDIR = CURFILE.parent.resolve()

if __name__ == '__main__':
    sys.path.insert(0, str(CURDIR.parent.parent.resolve()))

from wdom import options, tag
from wdom.themes import default
from wdom.document import Document, get_document


def _get_theme_name(theme) -> str:
    if hasattr(theme, 'name'):
        theme_name = theme.name
    elif theme.__name__ == 'wdom.themes':
        if options.config.theme:
            theme_name = options.config.theme.upper()
        else:
            theme_name = 'DEFAULT'
    return theme_name


def sample_app(theme=default) -> tag.Tag:
    app = theme.Div()
    app['style'] = '''\
        margin: 2em;
    '''
    body = theme.Container(parent=app)
    body.append(theme.Div(theme.H1(_get_theme_name(theme)),
                          style='text-align: center;'))
    body.append(theme.Hr())

    button_wrapper = theme.Div(parent=body)
    button_wrapper.append(
        theme.Button('Button'),
        theme.DefaultButton('Default'),
        theme.PrimaryButton('Primary'),
        theme.SecondaryButton('Secondary'),
        theme.SuccessButton('Success'),
        theme.InfoButton('Info'),
        theme.WarningButton('Warning'),
        theme.DangerButton('Danger'),
        theme.ErrorButton('Error'),
        theme.LinkButton('Link'),
    )
    body.append(theme.Hr())

    input_wrapper = theme.Form(parent=theme.FormGroup(parent=body))
    input_wrapper.append(
        theme.Textarea(placeholder='<textarea></textarea>'),
        theme.Input(placeholder='<input type="text">'),
        theme.Label(theme.CheckBox(id='checkbox1'), 'CheckBox 1'),
        theme.CheckBox(id='checkbox2'),
        theme.Label('CheckBox 2', **{'for':'checkbox2'}),
        theme.RadioButton(id='radio1', name='radio_group'),
        theme.Label('RadioButton 1', **{'for':'radio1'}),
        theme.RadioButton(id='radio2', name='radio_group'),
        theme.Label('RadioButton 2', **{'for':'radio2'}),
    )

    dropdown_list = theme.Select(parent=body)
    dropdown_list.append(
        theme.Option('Item 1'),
        theme.Optgroup(
            theme.Option('Item 2'),
            theme.Option('Item 3'),
            label='- Item Group -'
        )
    )
    multi_select = theme.Select(parent=body, multiple=True)
    multi_select.append(
        theme.Option('Option 1'),
        theme.Optgroup(
            theme.Option('Option 2'),
            theme.Option('Option 3'),
            label='- Option Group -'
        )
    )
    body.append(theme.Hr())

    # List
    list_div = theme.Row(parent=body)
    ul_div = theme.Col6(parent=list_div)
    ul_div.append(theme.H3('Unordered List'))
    ul1 = theme.Ul(parent=ul_div)
    ul1.append(theme.Li('Item 1'))
    li = theme.Li('Item 2', parent=ul1)
    ul2 = theme.Ul(parent=li)
    ul2.append(
        theme.Li('Item 2.1'),
        theme.Li('Item 2.2'),
        theme.Li('Item 3'),
    )

    ol_div = theme.Col6(parent=list_div)
    ol_div.append(theme.H3('Ordered List'))
    ol1 = theme.Ol(parent=ol_div)
    ol1.append(theme.Li('Item 1'))
    li = theme.Li('Item 2', parent=ol1)
    ol2 = theme.Ol(parent=li)
    ol2.append(
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

    grid = theme.Container(parent=body,
                           style='border: solid 1px #bbb; background-color: #666;')
    left_style = 'background-color: #eeeeee;'
    right_style = 'background-color: #fafafa'
    for i in range(0, 13):
        l = 'Col' + str(i or '')
        r = 'Col' + str(12 - i or '')
        grid.append(theme.Row(
            getattr(theme, l)(l, style=left_style),
            getattr(theme, r)(r, style=right_style),
        ))

    return app


def sample_page(theme=default) -> Document:
    page = get_document()
    app = sample_app(theme)
    page.body.prepend(app)
    for css in theme.css_files:
        page.add_cssfile(css)
    for js in theme.js_files:
        page.add_jsfile(js)
    return page


def main():
    import asyncio
    from wdom.server import start_server, get_app, stop_server
    doc = sample_page()
    app = get_app(document=doc)
    loop = asyncio.get_event_loop()
    server = start_server(app=app, loop=loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        stop_server(server)
        loop.close()


if __name__ == '__main__':
    main()
