#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '_static/css/kathamo.min.css',
]

class Button(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('data-role', 'button')


DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button)
SuccessButton = NewTag('DefaultButton', 'button', Button)
InfoButton = NewTag('InfoButton', 'button', Button)
WarningButton = NewTag('PrimaryButton', 'button', Button)
DangerButton = NewTag('PrimaryButton', 'button', Button)
LinkButton = NewTag('LinkButton', 'button', Button)

Row = NewTag('Row', 'div', class_='container')
Col1 = NewTag('Col', 'div', class_='col-sm-1 col-md-1 col-lg-1')
Col2 = NewTag('Col', 'div', class_='col-sm-2 col-md-2 col-lg-2')
Col3 = NewTag('Col', 'div', class_='col-sm-3 col-md-3 col-lg-3')
Col4 = NewTag('Col', 'div', class_='col-sm-4 col-md-4 col-lg-4')
Col5 = NewTag('Col', 'div', class_='col-sm-5 col-md-5 col-lg-5')
Col6 = NewTag('Col', 'div', class_='col-sm-6 col-md-6 col-lg-6')
Col7 = NewTag('Col', 'div', class_='col-sm-7 col-md-7 col-lg-7')
Col8 = NewTag('Col', 'div', class_='col-sm-8 col-md-8 col-lg-8')
Col9 = NewTag('Col', 'div', class_='col-sm-9 col-md-9 col-lg-9')
Col10 = NewTag('Col', 'div', class_='col-sm-10 col-md-10 col-lg-10')
Col11 = NewTag('Col', 'div', class_='col-sm-11 col-md-11 col-lg-11')
