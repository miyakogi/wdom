#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '_static/css/skyblue.min.css',
]


Button = NewTag('Button', 'a', bases=A, class_='btn')
DefaultButton = NewTag('DefaultButton', 'a', Button, class_='btn-dark')
PrimaryButton = NewTag('PrimaryButton', 'a', Button)
SuccessButton = NewTag('SuccessButton', 'a', Button, class_='btn-success')
InfoButton = NewTag('InfoButton', 'a', Button, class_='btn-empty')
WarningButton = NewTag('WarningButton', 'a', Button, class_='btn-warning')
DangerButton = NewTag('DangerButton', 'a', Button, class_='btn-error')
LinkButton = NewTag('LinkButton', 'a', Button, class_='btn-empty btn-success')

Input = NewTag('Input', 'input', Input, class_='form-control', type_='text')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-control')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='form-control')
Select = NewTag('Select', 'select', Select, class_='form-control')

Table = NewTag('Table', 'table', Table, class_='table')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='row')

Col1 = NewTag('Col', 'div', class_='col xs-1 sm-1 md-1 lg-1 xl-1')
Col2 = NewTag('Col', 'div', class_='col xs-2 sm-2 md-2 lg-2 xl-2')
Col3 = NewTag('Col', 'div', class_='col xs-3 sm-3 md-3 lg-3 xl-3')
Col4 = NewTag('Col', 'div', class_='col xs-4 sm-4 md-4 lg-4 xl-4')
Col5 = NewTag('Col', 'div', class_='col xs-5 sm-5 md-5 lg-5 xl-5')
Col6 = NewTag('Col', 'div', class_='col xs-6 sm-6 md-6 lg-6 xl-6')
Col7 = NewTag('Col', 'div', class_='col xs-7 sm-7 md-7 lg-7 xl-7')
Col8 = NewTag('Col', 'div', class_='col xs-8 sm-8 md-8 lg-8 xl-8')
Col9 = NewTag('Col', 'div', class_='col xs-9 sm-9 md-9 lg-9 xl-9')
Col10 = NewTag('Col', 'div', class_='col xs-10 sm-10 md-10 lg-10 xl-10')
Col11 = NewTag('Col', 'div', class_='col xs-11 sm-11 md-11 lg-11 xl-11')
