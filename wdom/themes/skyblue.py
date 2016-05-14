#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'SkyBlue'
project_url = 'http://stanko.github.io/skyblue/'
project_repository = 'https://github.com/Stanko/skyblue'
license = 'MIT License'
license_url = 'https://github.com/Stanko/skyblue/blob/gh-pages/LICENSE.md'

css_files = [
    '_static/css/skyblue.min.css',
]


Button = NewTag('Button', 'a', bases=A, class_='btn')
DefaultButton = NewTag('DefaultButton', 'a', Button, class_='btn-dark', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'a', Button, is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'a', Button, class_='btn-light', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'a', Button, class_='btn-success', is_='success-button')
InfoButton = NewTag('InfoButton', 'a', Button, class_='btn-empty', is_='info-button')
WarningButton = NewTag('WarningButton', 'a', Button, class_='btn-warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'a', Button, class_='btn-error', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'a', Button, class_='btn-error', is_='error-button')
LinkButton = NewTag('LinkButton', 'a', Button, class_='btn-empty btn-success', is_='link-button')

Input = NewTag('Input', 'input', Input, class_='form-control', type_='text')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-control')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-control')
Select = NewTag('Select', 'select', Select, class_='form-control')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row')

Col = NewTag('Col', 'div', Col, class_='col')
Col1 = NewTag('Col1', 'div', Col1, class_='col xs-1 sm-1 md-1 lg-1 xl-1')
Col2 = NewTag('Col2', 'div', Col2, class_='col xs-2 sm-2 md-2 lg-2 xl-2')
Col3 = NewTag('Col3', 'div', Col3, class_='col xs-3 sm-3 md-3 lg-3 xl-3')
Col4 = NewTag('Col4', 'div', Col4, class_='col xs-4 sm-4 md-4 lg-4 xl-4')
Col5 = NewTag('Col5', 'div', Col5, class_='col xs-5 sm-5 md-5 lg-5 xl-5')
Col6 = NewTag('Col6', 'div', Col6, class_='col xs-6 sm-6 md-6 lg-6 xl-6')
Col7 = NewTag('Col7', 'div', Col7, class_='col xs-7 sm-7 md-7 lg-7 xl-7')
Col8 = NewTag('Col8', 'div', Col8, class_='col xs-8 sm-8 md-8 lg-8 xl-8')
Col9 = NewTag('Col9', 'div', Col9, class_='col xs-9 sm-9 md-9 lg-9 xl-9')
Col10 = NewTag('Col10', 'div', Col10, class_='col xs-10 sm-10 md-10 lg-10 xl-10')
Col11 = NewTag('Col11', 'div', Col11, class_='col xs-11 sm-11 md-11 lg-11 xl-11')
Col12 = NewTag('Col12', 'div', Col12, class_='col xs-12 sm-12 md-12 lg-12 xl-12')

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
    Textarea,
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
