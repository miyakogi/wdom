#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Foundation'
project_url = 'http://foundation.zurb.com/'
project_repository = 'https://github.com/zurb/foundation-sites'
license = 'MIT License'
license_url = 'https://github.com/zurb/foundation-sites/blob/develop/LICENSE'

css_files = [
    '//cdn.jsdelivr.net/foundation/6.2.1/foundation.min.css',
]

js_files = [
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '//cdn.jsdelivr.net/foundation/6.2.1/foundation.min.js',
]

headers = []

Button = NewTag('Button', bases=Button, class_='button')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='hollow secondary', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='secondary', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='success hollow', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='warning', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='alert', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='alert', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='hollow', is_='link-button')

Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='columns')
Col1 = NewTag('Col1', 'div', Col, class_='small-1 medium-1 large-1', is_='col1')
Col2 = NewTag('Col2', 'div', Col, class_='small-2 medium-2 large-2', is_='col2')
Col3 = NewTag('Col3', 'div', Col, class_='small-3 medium-3 large-3', is_='col3')
Col4 = NewTag('Col4', 'div', Col, class_='small-4 medium-4 large-4', is_='col4')
Col5 = NewTag('Col5', 'div', Col, class_='small-5 medium-5 large-5', is_='col5')
Col6 = NewTag('Col6', 'div', Col, class_='small-6 medium-6 large-6', is_='col6')
Col7 = NewTag('Col7', 'div', Col, class_='small-7 medium-7 large-7', is_='col7')
Col8 = NewTag('Col8', 'div', Col, class_='small-8 medium-8 large-8', is_='col8')
Col9 = NewTag('Col9', 'div', Col, class_='small-9 medium-9 large-9', is_='col9')
Col10 = NewTag('Col10', 'div', Col, class_='small-10 medium-10 large-10', is_='col10')
Col11 = NewTag('Col11', 'div', Col, class_='small-11 medium-11 large-11', is_='col11')
Col12 = NewTag('Col12', 'div', Col, class_='small-12 medium-12 large-12', is_='col12')

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
    Col,
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
