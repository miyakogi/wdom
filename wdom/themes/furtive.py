#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Furtive'
project_url = 'http://furtive.co/'
project_repository = 'https://github.com/johnotander/furtive'
license = 'MIT License'
license_url = 'https://github.com/johnotander/furtive/blob/master/LICENSE'

css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/furtive/2.2.3/furtive.css',
]

Button = NewTag('Button', 'a', Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'a', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'a', Button, class_='btn--blue', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'a', Button, is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'a', Button, class_='btn--green', is_='success-button')
InfoButton = NewTag('InfoButton', 'a', Button, class_='btn--blue', is_='info-button')
WarningButton = NewTag('WarningButton', 'a', Button, class_='btn--red', is_='warning-button')
DangerButton = NewTag('DangerButton', 'a', Button, class_='btn--red', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'a', Button, class_='btn--red', is_='error-button')
LinkButton = NewTag('LinkButton', 'a', Button, class_='btn--link', is_='link-button')

Container = NewTag('Container', 'div', Container, class_='grd')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='grd')
Row = NewTag('Row', 'div', Row, class_='grd-row')
# Why 6 columns...
Col = NewTag('Col', 'div', Col)
Col1 = NewTag('Col1', 'div', Col1, class_='grd-row-col-1-6')
Col2 = NewTag('Col2', 'div', Col2, class_='grd-row-col-1-6')
Col3 = NewTag('Col3', 'div', Col3, class_='grd-row-col-2-6')
Col4 = NewTag('Col4', 'div', Col4, class_='grd-row-col-2-6')
Col5 = NewTag('Col5', 'div', Col5, class_='grd-row-col-3-6')
Col6 = NewTag('Col6', 'div', Col6, class_='grd-row-col-3-6')
Col7 = NewTag('Col7', 'div', Col7, class_='grd-row-col-4-6')
Col8 = NewTag('Col8', 'div', Col8, class_='grd-row-col-4-6')
Col9 = NewTag('Col9', 'div', Col9, class_='grd-row-col-5-6')
Col10 = NewTag('Col10', 'div', Col10, class_='grd-row-col-5-6')
Col11 = NewTag('Col11', 'div', Col11, class_='grd-row-col-5-6')


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
    Container,
    Wrapper,
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
]
