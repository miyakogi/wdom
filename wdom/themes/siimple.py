#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Siimple'
project_url = 'https://siimple.github.io/'
project_repository = 'https://github.com/siimple/siimple/'
license = 'MIT License'
license_url = 'https://github.com/siimple/siimple/blob/master/LICENSE.md'

css_files = [
    '_static/css/siimple.min.css',
]

PrimaryButton = NewTag('PrimaryButton', bases=Button, class_='btn', is_='primary-button')
SuccessButton = NewTag('SuccessButton', 'button', PrimaryButton, is_='success-button')
InfoButton = NewTag('InfoButton', 'button', PrimaryButton, is_='info-button')
WarningButton = NewTag('WarningButton', 'button', PrimaryButton, is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', PrimaryButton, is_='danger-button')
Button = NewTag('Button', bases=Button, class_='btn-outline')
DefaultButton = NewTag('Button', bases=Button, is_='default-button')
SecondaryButton = NewTag('SecondaryButton', bases=Button, is_='secondary-button')
LinkButton = NewTag('LinkButton', bases=Button, is_='link-button')

Input = NewTag('Input', 'input', Input, class_='form-input')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-input')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-textarea')
Select = NewTag('Select', 'select', Select, class_='form-select')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', Container, class_='grid grid-fluid')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='grid grid-fluid')
Row = NewTag('Row', 'div', Row, class_='row')

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
    PrimaryButton,
    SuccessButton,
    InfoButton,
    WarningButton,
    DangerButton,
    Button,
    DefaultButton,
    SecondaryButton,
    LinkButton,
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
