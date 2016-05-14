#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Schema'
project_url = 'http://danmalarkey.github.io/schema/'
project_repository = 'https://github.com/danmalarkey/schema'
license = 'MIT License & CC BY 3.0 (EasyDropdown)'
license_url = 'https://github.com/danmalarkey/schema#license'

css_files = [
    '_static/css/schema.min.css',
]

Button = NewTag('Button', bases=Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='btn-default', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='btn-primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='btn-default', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='btn-success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='btn-info', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='btn-warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='btn-danger', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='btn-danger', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='btn-link', is_='link-button')

FormGroup = NewTag('FormGroup', 'div', FormGroup, class_='form-group')
Input = NewTag('Input', 'input', Input, class_='form-element')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-element')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-element')
Select = NewTag('Select', 'select', Select, class_='form-element')

# Lists
# Ul = NewTag('Ul', 'ul', Ul, class_='list-group')
# Li = NewTag('Li', 'li', Li, class_='list-group-element')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row-fluid')

Col1 = NewTag('Col1', 'div', Col1, class_='col1')
Col2 = NewTag('Col2', 'div', Col2, class_='col2')
Col3 = NewTag('Col3', 'div', Col3, class_='col3')
Col4 = NewTag('Col4', 'div', Col4, class_='col4')
Col5 = NewTag('Col5', 'div', Col5, class_='col5')
Col6 = NewTag('Col6', 'div', Col6, class_='col6')
Col7 = NewTag('Col7', 'div', Col7, class_='col7')
Col8 = NewTag('Col8', 'div', Col8, class_='col8')
Col9 = NewTag('Col9', 'div', Col9, class_='col9')
Col10 = NewTag('Col10', 'div', Col10, class_='col10')
Col11 = NewTag('Col11', 'div', Col11, class_='col11')
Col12 = NewTag('Col12', 'div', Col12, class_='col12')

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
    FormGroup,
    Input,
    TextInput,
    Textarea,
    Select,
    Table,
    Container,
    Wrapper,
    Row,
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
