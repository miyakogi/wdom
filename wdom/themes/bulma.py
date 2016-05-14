#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Bulma'
project_url = 'http://bulma.io/'
project_repository = 'https://github.com/jgthms/bulma/'
license = 'MIT License'
license_url = 'https://github.com/jgthms/bulma/blob/master/LICENSE'

css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/bulma/0.0.20/css/bulma.min.css',
]

js_files = []
headers = []

Button = NewTag('Button', bases=Button, class_='button')
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='is-primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', PrimaryButton, class_='is-outlined', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='is-success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='is-info', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='is-warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='is-danger', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='is-danger', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='is-link', is_='link-button')

Input = NewTag('Input', 'input', Input)
TextInput = NewTag('Input', 'input', Input, type_='text', class_='input')
CheckBox = NewTag('Input', 'input', Input, type_='checkbox', class_='checkbox')
RadioButton = NewTag('Input', 'input', Input, type_='radio', class_='radio')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='textarea')

class Select(NestedTag):
    tag = 'span'
    class_ = 'select'
    inner_tag_class = Select
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inner_element.addEventListener('change', self.dispatchEvent)
        self._inner_element.addEventListener('click', self.dispatchEvent)

Table = NewTag('Table', 'table', Table, class_='table')

H1 = NewTag('H1', 'h1', H1, class_='title is-1')
H2 = NewTag('H2', 'h2', H2, class_='title is-2')
H3 = NewTag('H3', 'h3', H3, class_='title is-3')
H4 = NewTag('H4', 'h4', H4, class_='title is-4')
H5 = NewTag('H5', 'h5', H5, class_='title is-5')
H6 = NewTag('H6', 'h6', H6, class_='title is-6')

Container = NewTag('Container', 'div', Container, class_='content')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='content')
Row = NewTag('Row', 'div', Row, class_='columns')

Col = NewTag('Col', 'div', Col, class_='column')
Col1 = NewTag('Col1', 'div', Col, class_='is-1', is_='col1')
Col2 = NewTag('Col2', 'div', Col, class_='is-2', is_='col2')
Col3 = NewTag('Col3', 'div', Col, class_='is-3', is_='col3')
Col4 = NewTag('Col4', 'div', Col, class_='is-4', is_='col4')
Col5 = NewTag('Col5', 'div', Col, class_='is-5', is_='col5')
Col6 = NewTag('Col6', 'div', Col, class_='is-6', is_='col6')
Col7 = NewTag('Col7', 'div', Col, class_='is-7', is_='col7')
Col8 = NewTag('Col8', 'div', Col, class_='is-8', is_='col8')
Col9 = NewTag('Col9', 'div', Col, class_='is-9', is_='col9')
Col10 = NewTag('Col10', 'div', Col, class_='is-10', is_='col10')
Col11 = NewTag('Col11', 'div', Col, class_='is-11', is_='col11')
Col12 = NewTag('Col12', 'div', Col, class_='is-12', is_='col12')

extended_classes = [
    Button,
    DefaultButton,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    InfoButton,
    WarningButton,
    DangerButton,
    ErrorButton,
    LinkButton,
    Input,
    TextInput,
    CheckBox,
    RadioButton,
    Textarea,
    Select,
    Table,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
    Container,
    Wrapper,
    Row,
    Col,
    Col1,
    Col2,
    Col3,
    Col4,
    Col5,
    Col6,
    Col7,
    Col8,
    Col9,
    Col10,
    Col11,
    Col12,
]
