#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Pure'
project_url = 'http://purecss.io/'
project_repository = 'https://github.com/yahoo/pure/'
license = 'BSD License'
license_url = 'https://github.com/yahoo/pure/blob/master/LICENSE.md'

css_files = [
    '//yui.yahooapis.com/pure/0.6.0/pure-min.css',
    '_static/css/pure-extra.css',
]

Button = NewTag('Button', bases=Button, class_='pure-button')
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='pure-button-primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='pure-button-secondary', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='pure-button-success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='pure-button-secondary', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='pure-button-warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='pure-button-error', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='pure-button-error', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='pure-button-link', is_='link-button')

Form = NewTag('Form', 'form', Form, class_='pure-form')

Table = NewTag('Table', 'table', Table, class_='pure-table')

Row = NewTag('Row', 'div', Row, class_='pure-g')
Col1 = NewTag('Col1', 'div', Col1, class_='pure-u-2-24')
Col2 = NewTag('Col2', 'div', Col2, class_='pure-u-4-24')
Col3 = NewTag('Col3', 'div', Col3, class_='pure-u-6-24')
Col4 = NewTag('Col4', 'div', Col4, class_='pure-u-8-24')
Col5 = NewTag('Col5', 'div', Col5, class_='pure-u-10-24')
Col6 = NewTag('Col6', 'div', Col6, class_='pure-u-12-24')
Col7 = NewTag('Col7', 'div', Col7, class_='pure-u-14-24')
Col8 = NewTag('Col8', 'div', Col8, class_='pure-u-16-24')
Col9 = NewTag('Col9', 'div', Col9, class_='pure-u-18-24')
Col10 = NewTag('Col10', 'div', Col10, class_='pure-u-20-24')
Col11 = NewTag('Col11', 'div', Col11, class_='pure-u-22-24')
Col12 = NewTag('Col12', 'div', Col12, class_='pure-u-24-24')


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
    Col12,
]
