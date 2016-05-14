#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'INK'
project_url = 'http://ink.sapo.pt/'
project_repository = 'https://github.com/sapo/Ink/'
license = 'MIT License'
license_url = 'https://github.com/sapo/Ink/blob/develop/LICENSE'

css_files = [
    '//fastly.ink.sapo.pt/3.1.10/css/ink.css',
]
js_files = [
    '//fastly.ink.sapo.pt/3.1.10/js/ink-all.js',
]
headers = []

Button = NewTag('Button', 'button', Button, class_='ink-button')
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='blue', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='green', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='black', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='orange', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='red', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='red', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, is_='link-button')

Form = NewTag('Form', 'form', Form, class_='ink-form')
FormGroup = NewTag('FormGroup', 'div', Div, class_='control-group')
Input = NewTag('Input', 'input', Input)
TextInput = NewTag('TextInput', 'input', TextInput)
Textarea = NewTag('Textarea', 'textarea', Textarea)
Select = NewTag('Select', 'ul', Ul, class_='dropdown-menu')
Option = NewTag('Option', 'li', Li)

Table = NewTag('Table', 'table', Table, class_='ink-table')

Container = NewTag('Container', 'div', Container, class_='ink-grid')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='ink-grid')
Row = NewTag('Row', 'div', Row, class_='column-group')
Col1 = NewTag('Col1', 'div', Col1, class_='all-10')
Col2 = NewTag('Col2', 'div', Col2, class_='all-15')
Col3 = NewTag('Col3', 'div', Col3, class_='all-25')
Col4 = NewTag('Col4', 'div', Col4, class_='all-33')
Col5 = NewTag('Col5', 'div', Col5, class_='all-40')
Col6 = NewTag('Col6', 'div', Col6, class_='all-50')
Col7 = NewTag('Col7', 'div', Col7, class_='all-60')
Col8 = NewTag('Col8', 'div', Col8, class_='all-66')
Col9 = NewTag('Col9', 'div', Col9, class_='all-75')
Col10 = NewTag('Col10', 'div', Col10, class_='all-85')
Col11 = NewTag('Col11', 'div', Col11, class_='all-90')
Col12 = NewTag('Col12', 'div', Col12, class_='all-100')

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
    Form,
    FormGroup,
    Input,
    TextInput,
    Textarea,
    Select,
    Option,
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
