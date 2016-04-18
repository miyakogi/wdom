#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '_static/css/schema.min.css',
]

Button = NewTag('Button', bases=Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='btn-default')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='btn-primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='btn-success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='btn-info')
WarningButton = NewTag('WarningButton', 'button', Button, class_='btn-warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='btn-danger')
LinkButton = NewTag('LinkButton', 'button', Button, class_='btn-link')

FormGroup = NewTag('FormGroup', 'div', class_='form-group')
Input = NewTag('Input', 'input', Input, class_='form-element')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-element')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-element')
Select = NewTag('Select', 'select', Select, class_='form-element')

# Lists
# Ul = NewTag('Ul', 'ul', Ul, class_='list-group')
# Li = NewTag('Li', 'li', Li, class_='list-group-element')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', Row, class_='row-fluid')

Col1 = NewTag('Col1', 'div', Col, class_='col1')
Col2 = NewTag('Col2', 'div', Col, class_='col2')
Col3 = NewTag('Col3', 'div', Col, class_='col3')
Col4 = NewTag('Col4', 'div', Col, class_='col4')
Col5 = NewTag('Col5', 'div', Col, class_='col5')
Col6 = NewTag('Col6', 'div', Col, class_='col6')
Col7 = NewTag('Col7', 'div', Col, class_='col7')
Col8 = NewTag('Col8', 'div', Col, class_='col8')
Col9 = NewTag('Col9', 'div', Col, class_='col9')
Col10 = NewTag('Col10', 'div', Col, class_='col10')
Col11 = NewTag('Col11', 'div', Col, class_='col11')
Col12 = NewTag('Col12', 'div', Col, class_='col12')
