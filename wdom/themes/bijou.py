#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Bijou'
project_url = 'http://andhart.github.io/bijou/'
project_repository = 'https://github.com/andhart/bijou'
license = 'MIT License'
license_url = 'https://github.com/andhart/bijou/blob/master/LICENSE'

css_files = [
    '_static/css/bijou.min.css',
]

Button = NewTag('Button', bases=Button, class_='button small')
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='success', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='danger', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='danger', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='danger', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, is_='link-button')

Table = NewTag('Table', 'table', Table, class_='table')

Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='span')
Col1 = NewTag('Col1', 'div', (Col1, Col), class_='one')
Col2 = NewTag('Col2', 'div', (Col2, Col), class_='two')
Col3 = NewTag('Col3', 'div', (Col3, Col), class_='three')
Col4 = NewTag('Col4', 'div', (Col4, Col), class_='four')
Col5 = NewTag('Col5', 'div', (Col5, Col), class_='five')
Col6 = NewTag('Col6', 'div', (Col6, Col), class_='six')
Col7 = NewTag('Col7', 'div', (Col7, Col), class_='seven')
Col8 = NewTag('Col8', 'div', (Col8, Col), class_='eight')
Col9 = NewTag('Col9', 'div', (Col9, Col), class_='nine')
Col10 = NewTag('Col10', 'div', (Col10, Col), class_='ten')
Col11 = NewTag('Col11', 'div', (Col11, Col), class_='eleven')

extended_classes = [
    Button,
    DefaultButton,
    PrimaryButton,
    SuccessButton,
    InfoButton,
    WarningButton,
    DangerButton,
    ErrorButton,
    LinkButton,
    Table,
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
]
