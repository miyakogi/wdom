#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Concise'
project_url = 'http://http://concisecss.com/'
project_repository = 'https://github.com/ConciseCSS/concise.css'
license = 'MIT License'
license_url = 'https://github.com/ConciseCSS/concise.css/blob/master/LICENSE'

css_files = [
    '//cdn.concisecss.com/v3.4.0/concise.min.css',
]

js_files = []

headers = []

DefaultButton = NewTag('DefaultButton', 'button', DefaultButton)
PrimaryButton = NewTag('PrimaryButton', 'button', PrimaryButton, class_='bg--primary')
SecondaryButton = NewTag('SecondaryButton', 'button', SecondaryButton, class_='bg--success')
SuccessButton = NewTag('SuccessButton', 'button', SuccessButton, class_='bg--success')
InfoButton = NewTag('InfoButton', 'button', InfoButton, class_='button--flat')
WarningButton = NewTag('WarningButton', 'button', WarningButton, class_='bg--warning')
DangerButton = NewTag('DangerButton', 'button', DangerButton, class_='bg--error')
ErrorButton = NewTag('ErrorButton', 'button', ErrorButton, class_='bg--error')
LinkButton = NewTag('LinkButton', 'button', LinkButton, class_='button--flat')

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row')

class Col(Div):
    column = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.column:
            self.setAttribute('column', str(self.column))

Col1 = NewTag('Col1', 'div', Col, column=1, is_='col1')
Col2 = NewTag('Col2', 'div', Col, column=2, is_='col2')
Col3 = NewTag('Col3', 'div', Col, column=3, is_='col3')
Col4 = NewTag('Col4', 'div', Col, column=4, is_='col4')
Col5 = NewTag('Col5', 'div', Col, column=5, is_='col5')
Col6 = NewTag('Col6', 'div', Col, column=6, is_='col6')
Col7 = NewTag('Col7', 'div', Col, column=7, is_='col7')
Col8 = NewTag('Col8', 'div', Col, column=8, is_='col8')
Col9 = NewTag('Col9', 'div', Col, column=9, is_='col9')
Col10 = NewTag('Col10', 'div', Col, column=10, is_='col10')
Col11 = NewTag('Col11', 'div', Col, column=11, is_='col11')
Col12 = NewTag('Col12', 'div', Col, column=12, is_='col12')

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
    Col12,
]
