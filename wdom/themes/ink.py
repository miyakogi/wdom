#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://ink.sapo.pt/'
project_repository = 'https://github.com/sapo/Ink/'

css_files = [
    '//fastly.ink.sapo.pt/3.1.10/css/ink.css',
]
js_files = [
    '//fastly.ink.sapo.pt/3.1.10/js/ink-all.js',
]
headers = []


Button = NewTag('Button', 'button', Button, class_='ink-button')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='blue')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='green')
InfoButton = NewTag('InfoButton', 'button', Button, class_='black')
WarningButton = NewTag('WarningButton', 'button', Button, class_='orange')
DangerButton = NewTag('DangerButton', 'button', Button, class_='red')
LinkButton = NewTag('LinkButton', 'button', Button)

Form = NewTag('Form', 'form', Form, class_='ink-form')
FormGroup = NewTag('FormGroup', 'div', Div, class_='control-group')
Input = NewTag('Input', 'input', Input)
TextInput = NewTag('TextInput', 'input', TextInput)
Textarea = NewTag('Textarea', 'textarea', Textarea)
Select = NewTag('Select', 'ul', Ul, class_='dropdown-menu')
Option = NewTag('Option', 'li', Li)

Table = NewTag('Table', 'table', Table, class_='ink-table')

Container = NewTag('Container', 'div', class_='ink-grid')
Wrapper = Container
Row = NewTag('Row', 'div', Row, class_='column-group')
Col1 = NewTag('Col1', 'div', Col, class_='all-10')
Col2 = NewTag('Col2', 'div', Col, class_='all-15')
Col3 = NewTag('Col3', 'div', Col, class_='all-25')
Col4 = NewTag('Col4', 'div', Col, class_='all-33')
Col5 = NewTag('Col5', 'div', Col, class_='all-40')
Col6 = NewTag('Col6', 'div', Col, class_='all-50')
Col7 = NewTag('Col7', 'div', Col, class_='all-60')
Col8 = NewTag('Col8', 'div', Col, class_='all-66')
Col9 = NewTag('Col9', 'div', Col, class_='all-75')
Col10 = NewTag('Col10', 'div', Col, class_='all-85')
Col11 = NewTag('Col11', 'div', Col, class_='all-90')
Col12 = NewTag('Col12', 'div', Col, class_='all-100')
