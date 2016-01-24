#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.dom import NewTagClass
from wdom.dom import *


css_files = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css'
]

js_files = [
    'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js',
]

headers = []

NewNode = NewTagClass

Button = NewNode('Button', bases=Button, class_='btn')
DefaultButton = NewNode('DefaultButton', bases=Button, class_='btn-default')
PrimaryButton = NewNode('PrimaryButton', bases=Button, class_='btn-primary')
SuccessButton = NewNode('SuccessButton', bases=Button, class_='btn-success')
InfoButton = NewNode('InfoButton', bases=Button, class_='btn-info')
WarningButton = NewNode('WarningButton', bases=Button, class_='btn-warning')
DangerButton = NewNode('DangerButton', bases=Button, class_='btn-danger')
LinkButton = NewNode('LinkButton', bases=Button, class_='btn-link')

FormGroup = NewNode('FormGroup', bases=Div, class_='form-group')
TextInput = NewNode('TextInput', bases=TextInput, class_='form-control')
TextArea = NewNode('TextArea', bases=TextArea, class_='form-control')
Select = NewNode('Select', bases=Select, class_='form-control')

Container = NewNode('Container', bases=Div, class_='container')
Wrapper = Container
Row = NewNode('Row', bases=Div, class_='row')
