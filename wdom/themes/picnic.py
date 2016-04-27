#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Picnic'
project_url = 'http://picnicss.com/'
project_repository = 'https://github.com/picnicss/picnic'
license = 'MIT License'
license_url = 'https://github.com/picnicss/picnic/blob/master/LICENSE'

css_files = [
    '//cdn.jsdelivr.net/picnicss/5.1.0/picnic.min.css',
]

Button = NewTag('Button', bases=Button)
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='error', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='error', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='pseudo', is_='link-button')

Row = NewTag('Row', 'div', Row, class_='row')
Col1 = NewTag('Col1', 'div', Col1)
Col2 = NewTag('Col2', 'div', Col2)
Col3 = NewTag('Col3', 'div', Col3, class_='fourth')
Col4 = NewTag('Col4', 'div', Col4, class_='third')
Col5 = NewTag('Col5', 'div', Col5)
Col6 = NewTag('Col6', 'div', Col6, class_='half')
Col7 = NewTag('Col7', 'div', Col7)
Col8 = NewTag('Col8', 'div', Col8, class_='two-third')
Col9 = NewTag('Col9', 'div', Col9, class_='three-fourth')
Col10 = NewTag('Col10', 'div', Col10)
Col11 = NewTag('Col11', 'div', Col11)
Col12 = NewTag('Col12', 'div', Col12)

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
    Col12,
]
