#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Papier'
project_url = 'http://gugel.io/papier/'
project_repository = 'https://github.com/alexanderGugel/papier'
license = 'MIT License'
license_url = 'https://github.com/alexanderGugel/papier/blob/master/LICENSE.md'

css_files = [
    '//cdn.rawgit.com/alexanderGugel/papier/master/dist/papier-1.0.0.min.css',
]

DefaultButton = NewTag('DefaultButton', 'button', Button, class_='bg-white')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='bg-blue')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='bg-grey')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='bg-light-blue')
InfoButton = NewTag('InfoButton', 'button', Button, class_='bg-green')
WarningButton = NewTag('WarningButton', 'button', Button, class_='bg-orange')
DangerButton = NewTag('DangerButton', 'button', Button, class_='bg-red')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='bg-red')
LinkButton = NewTag('LinkButton', 'button', Button, class_='bg-cyan')

Row = NewTag('Row', 'div', Row, class_='row')
Col1 = NewTag('Col1', 'div', Col1, class_='col-1')
Col2 = NewTag('Col2', 'div', Col2, class_='col-2')
Col3 = NewTag('Col3', 'div', Col3, class_='col-3')
Col4 = NewTag('Col4', 'div', Col4, class_='col-4')
Col5 = NewTag('Col5', 'div', Col5, class_='col-5')
Col6 = NewTag('Col6', 'div', Col6, class_='col-6')
Col7 = NewTag('Col7', 'div', Col7, class_='col-7')
Col8 = NewTag('Col8', 'div', Col8, class_='col-8')
Col9 = NewTag('Col9', 'div', Col9, class_='col-9')
Col10 = NewTag('Col10', 'div', Col10, class_='col-10')
Col11 = NewTag('Col11', 'div', Col11, class_='col-11')
Col12 = NewTag('Col12', 'div', Col12, class_='col-12')

extended_classes = [
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
