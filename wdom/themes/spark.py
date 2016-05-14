#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Spark'
project_url = 'http://codewithspark.com/'
project_repository = 'https://github.com/twistedpixel/spark/'
license = 'MIT License'
license_url = 'https://github.com/twistedpixel/spark/blob/master/dist/LICENSE'

css_files = [
    '_static/css/spark.min.css',
]

js_files = [
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '_static/js/spark.min.js',
]

headers = []

Button = NewTag('Button', bases=Button, class_='btn flat')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='black', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='blue', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='green', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='lime', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='green', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='orange', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='red', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='red', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='flat', is_='link-button')

class Form(Form):
    class_ = 'form'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('role', 'form')

Table = NewTag('Table', 'table', Table, class_='tbl')

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='col')
Col1 = NewTag('Col1', 'div', Col1, class_='col of-1')
Col2 = NewTag('Col2', 'div', Col2, class_='col of-2')
Col3 = NewTag('Col3', 'div', Col3, class_='col of-3')
Col4 = NewTag('Col4', 'div', Col4, class_='col of-4')
Col5 = NewTag('Col5', 'div', Col5, class_='col of-5')
Col6 = NewTag('Col6', 'div', Col6, class_='col of-6')
Col7 = NewTag('Col7', 'div', Col7, class_='col of-7')
Col8 = NewTag('Col8', 'div', Col8, class_='col of-8')
Col9 = NewTag('Col9', 'div', Col9, class_='col of-9')
Col10 = NewTag('Col10', 'div', Col10, class_='col of-10')
Col11 = NewTag('Col11', 'div', Col11, class_='col of-11')
Col12 = NewTag('Col12', 'div', Col12, class_='col of-12')

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
