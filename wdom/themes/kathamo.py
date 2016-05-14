#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'KATHAMO'
project_url = 'http://kathamo.github.io/'
project_repository = 'https://github.com/kathamo/Kathamo'
license = 'MIT License'
license_url = 'https://github.com/kathamo/Kathamo/blob/master/LICENSE'

css_files = [
    '_static/css/kathamo.min.css',
]

class Button(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('data-role', 'button')


DefaultButton = NewTag('DefaultButton', 'button', DefaultButton)
PrimaryButton = NewTag('PrimaryButton', 'button', PrimaryButton)
SecondaryButton = NewTag('DefaultButton', 'button', SecondaryButton)
SuccessButton = NewTag('DefaultButton', 'button', SuccessButton)
InfoButton = NewTag('InfoButton', 'button', InfoButton)
WarningButton = NewTag('WarningButton', 'button', WarningButton)
DangerButton = NewTag('DangerButton', 'button', DangerButton)
ErrorButton = NewTag('ErrorButton', 'button', ErrorButton)
LinkButton = NewTag('LinkButton', 'button', LinkButton)

Row = NewTag('Row', 'div', Row, class_='container')
Col1 = NewTag('Col1', 'div', Col1, class_='col-sm-1 col-md-1 col-lg-1')
Col2 = NewTag('Col2', 'div', Col2, class_='col-sm-2 col-md-2 col-lg-2')
Col3 = NewTag('Col3', 'div', Col3, class_='col-sm-3 col-md-3 col-lg-3')
Col4 = NewTag('Col4', 'div', Col4, class_='col-sm-4 col-md-4 col-lg-4')
Col5 = NewTag('Col5', 'div', Col5, class_='col-sm-5 col-md-5 col-lg-5')
Col6 = NewTag('Col6', 'div', Col6, class_='col-sm-6 col-md-6 col-lg-6')
Col7 = NewTag('Col7', 'div', Col7, class_='col-sm-7 col-md-7 col-lg-7')
Col8 = NewTag('Col8', 'div', Col8, class_='col-sm-8 col-md-8 col-lg-8')
Col9 = NewTag('Col9', 'div', Col9, class_='col-sm-9 col-md-9 col-lg-9')
Col10 = NewTag('Col10', 'div', Col10, class_='col-sm-10 col-md-10 col-lg-10')
Col11 = NewTag('Col11', 'div', Col11, class_='col-sm-11 col-md-11 col-lg-11')

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
]
