#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    body = theme.Container(parent=app, style='width: 80vw; margin: 1em 10vw;')
    body.append(theme.Div(theme.H1(_get_theme_name(theme)),
                          style='text-align: center;'))
    body.append(theme.Hr())

    # Typography
    body.append(theme.H1('Typography', style='text-align: center;'))
    typography = theme.Div(parent=body)
    typography.append(
        theme.H1('Heading 1'),
        theme.H2('Heading 2'),
        theme.H3('Heading 3'),
        theme.H4('Heading 4'),
        theme.H5('Heading 5'),
        theme.H6('Heading 6'),
        theme.P(
            'This is a paragraph. ',
            theme.Code('Code, '),
            theme.Strong('Bolded, '),
            theme.Em('Italicized, '),
            theme.A('Colored (link)'),
            ', and ',
            theme.U('Underlined'),
            ' strings.',
        ),
    )

    code_div = theme.Div(parent=body)
    pre = theme.Pre(parent=code_div)
    pre.append(theme.Code(
        '''\
    # Source code preview
    def python(i: int) -> str:
        print(str(i))
    '''.rstrip()))

    body.append(theme.Hr())

    # Buttons
    body.append(theme.H1('Buttons', style='text-align: center;'))

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

    # List
    body.append(theme.H1('List', style='text-align: center;'))
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

    # Form
    body.append(theme.H1('Form', style='text-align: center;'))

    input_wrapper = theme.FormInner(parent=theme.Form(parent=theme.FormGroup(parent=body)))  # noqa: E501
    input_wrapper.append(
        theme.Row(
            theme.Col6(
                theme.FormItem(
                    theme.Label('TextArea'),
                    theme.Textarea(placeholder='textarea', rows=10),
                ),
            ),
            theme.Col6(
                theme.FormItem(
                    theme.Label('Text Input'),
                    theme.Input(placeholder='<input type="text">'),
                ),
                theme.FormItem(
                    theme.Label(theme.CheckBox(), 'Check1'),
                    theme.Label(theme.CheckBox(), 'Check2'),
                ),
                theme.FormItem(
                    theme.Label(theme.RadioButton(name='radio_group'), 'Radio1'),  # noqa: E501
                    theme.Label(theme.RadioButton(name='radio_group'), 'Radio2'),  # noqa: E501
                ),
                theme.FormItem(
                    theme.Select(
                        theme.Option('Item 1'),
                        theme.Optgroup(
                            theme.Option('Item 2'),
                            theme.Option('Item 3'),
                            label='- Item Group -'
                        )
                    ),
                ),
                theme.FormItem(
                    theme.Select(
                        theme.Option('Option 1'),
                        theme.Optgroup(
                            theme.Option('Option 1.1'),
                            theme.Option('Option 1.2'),
                            theme.Option('Option 1.3'),
                            label='- Option Group -',
                        ),
                        multiple=True,
                        size=5,
                    ),
                ),
            ),
        ),
    )

    body.append(theme.Hr())

    # Table
    body.append(theme.H1('Table', style='text-align: center;'))

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
        theme.Td('Taro Suzuki'),
        theme.Td('26'),
        theme.Td('Male'),
        theme.Td('Tokyo'),
    )

    tr3 = theme.Tr(parent=tbody)
    tr3.append(
        theme.Td('Hanako Yamada'),
        theme.Td('20'),
        theme.Td('Female'),
        theme.Td('Kyoto'),
    )
    body.append(theme.Hr())

    # Grid Layout
    body.append(theme.H1('Grid Layout', style='text-align: center;'))

    grid = theme.Container(
        parent=body,
        style='border: solid 1px #bbb; background-color: #666;'
    )
    left_style = 'background-color: #eeeeee;'
    right_style = 'background-color: #fafafa'
    for i in range(0, 13):
        lcol = 'Col' + str(i or '')
        rcol = 'Col' + str(12 - i or '')
        grid.append(theme.Row(
            getattr(theme, lcol)(lcol, style=left_style),
            getattr(theme, rcol)(rcol, style=right_style),
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
    from wdom import server
    sample_page()
    server.start()


if __name__ == '__main__':
    main()
