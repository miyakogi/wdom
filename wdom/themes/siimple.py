#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '_static/css/siimple.min.css',
]

PrimaryButton = NewTag('Button', bases=Button, class_='btn')
SuccessButton = NewTag('SuccessButton', 'button', PrimaryButton)
InfoButton = NewTag('InfoButton', 'button', PrimaryButton)
WarningButton = NewTag('WarningButton', 'button', PrimaryButton)
DangerButton = NewTag('DangerButton', 'button', PrimaryButton)
Button = NewTag('Button', bases=Button, class_='btn-outline')
DefaultButton = NewTag('Button', bases=Button)
LinkButton = NewTag('Button', bases=Button)

Input = NewTag('Input', 'input', Input, class_='form-input')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-input')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-textarea')
Select = NewTag('Select', 'select', Select, class_='form-select')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', class_='grid grid-fluid')
Wrapper = Container
Row = NewTag('Row', 'div', Row, class_='row')

Col1 = NewTag('Col1', 'div', Col, class_='col-1')
Col2 = NewTag('Col2', 'div', Col, class_='col-2')
Col3 = NewTag('Col3', 'div', Col, class_='col-3')
Col4 = NewTag('Col4', 'div', Col, class_='col-4')
Col5 = NewTag('Col5', 'div', Col, class_='col-5')
Col6 = NewTag('Col6', 'div', Col, class_='col-6')
Col7 = NewTag('Col7', 'div', Col, class_='col-7')
Col8 = NewTag('Col8', 'div', Col, class_='col-8')
Col9 = NewTag('Col9', 'div', Col, class_='col-9')
Col10 = NewTag('Col10', 'div', Col, class_='col-10')
Col11 = NewTag('Col11', 'div', Col, class_='col-11')
Col12 = NewTag('Col12', 'div', Col, class_='col-12')
