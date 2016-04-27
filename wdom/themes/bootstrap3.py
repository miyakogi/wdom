#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Bootstrap3'
project_url = 'http://getbootstrap.com/'
project_repository = 'https://github.com/twbs/bootstrap'
license = 'MIT License'
license_url = 'https://github.com/twbs/bootstrap/blob/master/LICENSE'

css_files = [
    '//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css',
]

js_files = [
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js',
]

headers = []

Button = NewTag('Button', 'button', bases=Button, class_='btn')
# Inherit Button class defined here, to inherit 'btn' class
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='btn-default', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='btn-primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='btn-secondary', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='btn-success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='btn-info', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='btn-warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='btn-danger', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='btn-danger', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='btn-link', is_='link-button')

FormGroup = NewTag('FormGroup', 'div', FormGroup, class_='form-group')
Input = NewTag('Input', 'input', Input, class_='form-control')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-control')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-control')
Select = NewTag('Select', 'select', Select, class_='form-control')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row')

Col1 = NewTag('Col1', 'div', Col1, class_='col-xs-1 col-sm-1 col-md-1 col-lg-1')
Col2 = NewTag('Col2', 'div', Col2, class_='col-xs-2 col-sm-2 col-md-2 col-lg-2')
Col3 = NewTag('Col3', 'div', Col3, class_='col-xs-3 col-sm-3 col-md-3 col-lg-3')
Col4 = NewTag('Col4', 'div', Col4, class_='col-xs-4 col-sm-4 col-md-4 col-lg-4')
Col5 = NewTag('Col5', 'div', Col5, class_='col-xs-5 col-sm-5 col-md-5 col-lg-5')
Col6 = NewTag('Col6', 'div', Col6, class_='col-xs-6 col-sm-6 col-md-6 col-lg-6')
Col7 = NewTag('Col7', 'div', Col7, class_='col-xs-7 col-sm-7 col-md-7 col-lg-7')
Col8 = NewTag('Col8', 'div', Col8, class_='col-xs-8 col-sm-8 col-md-8 col-lg-8')
Col9 = NewTag('Col9', 'div', Col9, class_='col-xs-9 col-sm-9 col-md-9 col-lg-9')
Col10 = NewTag('Col10', 'div', Col10, class_='col-xs-10 col-sm-10 col-md-10 col-lg-10')
Col11 = NewTag('Col11', 'div', Col11, class_='col-xs-11 col-sm-11 col-md-11 col-lg-11')

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
]
