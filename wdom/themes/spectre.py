#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa

from wdom.tag import NewTagClass as NewTag
from wdom.themes import *

name = 'Spectre'
project_url = 'https://picturepan2.github.io/spectre'
project_repository = 'https://github.com/picturepan2/spectre'
license = 'MIT License'
license_url = 'https://github.com/picturepan2/spectre/blob/master/LICENSE'

css_files = [
    '_static/css/spectre.min.css',
]

Button = NewTag('Button', bases=Button, class_='btn')
DefaultButton = NewTag('Button', bases=Button)
PrimaryButton = NewTag('PrimaryButton', bases=Button, class_='btn-primary')
SecondaryButton = NewTag('SecondaryButton', bases=Button)
SuccessButton = NewTag('SuccessButton', 'button', Button)
InfoButton = NewTag('InfoButton', 'button', Button)
WarningButton = NewTag('WarningButton', 'button', PrimaryButton)
DangerButton = NewTag('DangerButton', 'button', PrimaryButton)
ErrorButton = NewTag('ErrorButton', 'button', PrimaryButton)
LinkButton = NewTag('LinkButton', bases=Button, class_='btn-link')

FormGroup = NewTag('FormGroup', 'div', FormGroup)
FormInner = NewTag('FormInner', 'div', FormGroup, class_='form-group')
Select = NewTag('Select', 'select', Select, class_='form-select')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='columns')
Col = NewTag('Col', 'div', Col, class_='col')
Col1 = NewTag('Col1', 'div', Col1, class_='col-1')
Col2 = NewTag('Col2', 'div', Col2, class_='col-2')
Col3 = NewTag('Col3', 'div', Col3, class_='col-3')
Col4 = NewTag('Col4', 'div', Col4, class_='col-4')
Col5 = NewTag('Col5', 'div', Col5, class_='col-5')
Col6 = NewTag('Col6', 'div', Col6, class_='col-6')
Col7 = NewTag('Col7', 'div', Col7, class_='col-7')
Col8 = NewTag('Col8', 'div', Col8, class_='col-8')
Col9 = NewTag('Col9', 'div', Col9, class_='col-9')
Col10 = NewTag('Col10', 'div', Col10, class_='col-10')
Col11 = NewTag('Col11', 'div', Col11, class_='col-11')
Col12 = NewTag('Col12', 'div', Col12, class_='col-12')

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
    Select,
    Table,
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
