#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/bulma/0.0.20/css/bulma.min.css',
]

js_files = []
headers = []

Button = NewTag('Button', bases=Button, class_='button')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='is-primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='is-success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='is-info')
WarningButton = NewTag('WarningButton', 'button', Button, class_='is-warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='is-danger')
LinkButton = NewTag('LinkButton', 'button', Button, class_='is-link')

Input = NewTag('Input', 'input', Input, class_='input')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='textarea')
Select = NewTag('Select', 'select', Select, class_='form-control')

Table = NewTag('Table', 'table', Table, class_='table')

H1 = NewTag('H1', 'h1', H1, class_='title is-1')
H2 = NewTag('H2', 'h2', H2, class_='title is-2')
H3 = NewTag('H3', 'h3', H3, class_='title is-3')
H4 = NewTag('H4', 'h4', H4, class_='title is-4')
H5 = NewTag('H5', 'h5', H5, class_='title is-5')
H6 = NewTag('H6', 'h6', H6, class_='title is-6')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='columns')

Col1 = NewTag('Col', 'div', class_='is-1')
Col2 = NewTag('Col', 'div', class_='is-2')
Col3 = NewTag('Col', 'div', class_='is-3')
Col4 = NewTag('Col', 'div', class_='is-4')
Col5 = NewTag('Col', 'div', class_='is-5')
Col6 = NewTag('Col', 'div', class_='is-6')
Col7 = NewTag('Col', 'div', class_='is-7')
Col8 = NewTag('Col', 'div', class_='is-8')
Col9 = NewTag('Col', 'div', class_='is-9')
Col10 = NewTag('Col', 'div', class_='is-10')
Col11 = NewTag('Col', 'div', class_='is-11')
