#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css'
]

js_files = [
    'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js',
]

headers = []

Button = NewTag('Button', bases=Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='btn-default')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='btn-primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='btn-success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='btn-info')
WarningButton = NewTag('WarningButton', 'button', Button, class_='btn-warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='btn-danger')
LinkButton = NewTag('LinkButton', 'button', Button, class_='btn-link')

FormGroup = NewTag('FormGroup', 'div', class_='form-group')
TextInput = NewTag('TextInput', 'input', TextInput, class_='form-control')
TextArea = NewTag('TextArea', 'textarea', TextArea, class_='form-control')
Select = NewTag('Select', 'select', Select, class_='form-control')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='row')

Col1 = NewTag('Col', 'div', class_='col-xs-1 col-sm-1 col-md-1 col-lg-1')
Col2 = NewTag('Col', 'div', class_='col-xs-2 col-sm-2 col-md-2 col-lg-2')
Col3 = NewTag('Col', 'div', class_='col-xs-3 col-sm-3 col-md-3 col-lg-3')
Col4 = NewTag('Col', 'div', class_='col-xs-4 col-sm-4 col-md-4 col-lg-4')
Col5 = NewTag('Col', 'div', class_='col-xs-5 col-sm-5 col-md-5 col-lg-5')
Col6 = NewTag('Col', 'div', class_='col-xs-6 col-sm-6 col-md-6 col-lg-6')
Col7 = NewTag('Col', 'div', class_='col-xs-7 col-sm-7 col-md-7 col-lg-7')
Col8 = NewTag('Col', 'div', class_='col-xs-8 col-sm-8 col-md-8 col-lg-8')
Col9 = NewTag('Col', 'div', class_='col-xs-9 col-sm-9 col-md-9 col-lg-9')
Col10 = NewTag('Col', 'div', class_='col-xs-10 col-sm-10 col-md-10 col-lg-10')
Col11 = NewTag('Col', 'div', class_='col-xs-11 col-sm-11 col-md-11 col-lg-11')
