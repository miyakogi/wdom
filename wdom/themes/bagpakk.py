#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa

from wdom.tag import NewTagClass as NewTag
from wdom.themes import *

name = 'Bagpakk'
project_url = 'http://brutaldesign.github.io/bagpakk/'
project_repository = 'https://github.com/brutaldesign/bagpakk/'
license = 'MIT License'
license_url = 'https://github.com/brutaldesign/bagpakk/blob/master/LICENSE'

css_files = [
    '_static/css/bagpakk.min.css',
]

Button = NewTag('Button', 'a', class_='button-alt', is_='button')
DefaultButton = NewTag('DefaultButton', 'a', class_='button-alt', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'a', class_='button', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'a', class_='button-alt', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'a', class_='button', is_='success-button')
InfoButton = NewTag('InfoButton', 'a', class_='button-alt', is_='info-button')
WarningButton = NewTag('WarningButton', 'a', class_='button', is_='warning-button')
DangerButton = NewTag('DangerButton', 'a', class_='button', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'a', class_='button', is_='error-button')
LinkButton = NewTag('LinkButton', 'a', class_='button-alt', is_='link-button')

Col1 = NewTag('Col1', 'div', Col, class_='col-1', is_='col1')
Col2 = NewTag('Col2', 'div', Col, class_='col-2', is_='col2')
Col3 = NewTag('Col3', 'div', Col, class_='col-3', is_='col3')
Col4 = NewTag('Col4', 'div', Col, class_='col-4', is_='col4')
Col5 = NewTag('Col5', 'div', Col, class_='col-5', is_='col5')
Col6 = NewTag('Col6', 'div', Col, class_='col-6', is_='col6')
Col7 = NewTag('Col7', 'div', Col, class_='col-7', is_='col7')
Col8 = NewTag('Col8', 'div', Col, class_='col-8', is_='col8')
Col9 = NewTag('Col9', 'div', Col, class_='col-9', is_='col9')
Col10 = NewTag('Col10', 'div', Col, class_='col-10', is_='col10')
Col11 = NewTag('Col11', 'div', Col, class_='col-11', is_='col11')
Col12 = NewTag('Col12', 'div', Col, class_='col-12', is_='col12')

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
