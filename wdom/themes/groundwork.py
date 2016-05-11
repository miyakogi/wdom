#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Groundwork'
project_url = 'https://groundworkcss.github.io/groundwork/'
project_repository = 'https://github.com/groundworkcss/groundwork'
license = 'MIT License'
license_url = 'https://github.com/groundworkcss/groundwork/blob/master/LICENSE'

css_files = [
    '_static/css/groundwork.css',
]

js_files = [
    '//cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js',
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '_static/js/groundwork.all.js',
]

Button = NewTag('Button', bases=Button)
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='blue', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='turquoise', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='info', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='error', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='error', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='green', is_='link-button')

Row = NewTag('Row', 'div', Row, class_='row')
Col1 = NewTag('Col1', 'div', Col1, class_='one twelfth')
Col2 = NewTag('Col2', 'div', Col2, class_='one sixth')
Col3 = NewTag('Col3', 'div', Col3, class_='one fourth')
Col4 = NewTag('Col4', 'div', Col4, class_='one third')
Col5 = NewTag('Col5', 'div', Col5, class_='five twelfths')
Col6 = NewTag('Col6', 'div', Col6, class_='one half')
Col7 = NewTag('Col7', 'div', Col7, class_='seven twelfths')
Col8 = NewTag('Col8', 'div', Col8, class_='two thirds')
Col9 = NewTag('Col9', 'div', Col9, class_='three fourths')
Col10 = NewTag('Col10', 'div', Col10, class_='five sixths')
Col11 = NewTag('Col11', 'div', Col11, class_='eleven twelfths')

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
