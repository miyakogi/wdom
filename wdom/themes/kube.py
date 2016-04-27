#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Kube'
project_url = 'https://imperavi.com/kube/'
project_repository = 'https://github.com/imperavi/kube'
license = 'MIT License'
license_url = 'https://imperavi.com/kube/#kube-intro'

css_files = [
    '_static/css/kube.min.css',
]


class TypedButton(Button):
    type_ = None
    outline = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type_:
            self.setAttribute('type', self.type_)
        if self.outline:
            self.setAttribute('outline', True)

DefaultButton = NewTag('DefaultButton', 'button', TypedButton, type_='black',
                       outline=True, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', TypedButton, type_='primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', TypedButton, type_='black',
                         outline=True, is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', TypedButton, type_='black', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', TypedButton, type_='primary',
                    outline=True, is_='info-button')
WarningButton = NewTag('WarningButton', 'button', TypedButton, is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', TypedButton, is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', TypedButton, is_='error-button')
LinkButton = NewTag('LinkButton', 'button', TypedButton, outline=True, is_='link-button')

Form = NewTag('Form', 'form', Form, class_='forms')
Select = NewTag('Select', 'select', Select, class_='select')

Row = NewTag('Row', 'row', Row)

class Col(Div):
    tag = 'column'
    cols = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('cols', str(self.cols))

Col1 = NewTag('Col1', 'column', Col, is_='col1')
Col2 = NewTag('Col2', 'column', Col, cols=2, is_='col2')
Col3 = NewTag('Col3', 'column', Col, cols=3, is_='col3')
Col4 = NewTag('Col4', 'column', Col, cols=4, is_='col4')
Col5 = NewTag('Col5', 'column', Col, cols=5, is_='col5')
Col6 = NewTag('Col6', 'column', Col, cols=6, is_='col6')
Col7 = NewTag('Col7', 'column', Col, cols=7, is_='col7')
Col8 = NewTag('Col8', 'column', Col, cols=8, is_='col8')
Col9 = NewTag('Col9', 'column', Col, cols=9, is_='col9')
Col10 = NewTag('Col10', 'column', Col, cols=10, is_='col10')
Col11 = NewTag('Col11', 'column', Col, cols=11, is_='col11')
Col12 = NewTag('Col12', 'column', Col, cols=12, is_='col12')

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
    Form,
    Select,
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
