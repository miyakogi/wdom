#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://furtive.co/'
project_repository = 'https://github.com/johnotander/furtive'

css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/furtive/2.2.3/furtive.css',
]

Button = NewTag('Button', 'a', Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'a', Button)
PrimaryButton = NewTag('PrimaryButton', 'a', Button, class_='btn--blue')
SuccessButton = NewTag('SuccessButton', 'a', Button, class_='btn--green')
InfoButton = NewTag('InfoButton', 'a', Button, class_='btn--blue')
WarningButton = NewTag('WarningButton', 'a', Button, class_='btn--red')
DangerButton = NewTag('DangerButton', 'a', Button, class_='btn--red')
LinkButton = NewTag('LinkButton', 'a', Button, class_='btn--link')

Container = NewTag('Container', 'div', Container, class_='grd')
Row = NewTag('Row', 'div', Row, class_='grd-row')
# Why 6 columns...
Col = NewTag('Col', 'div', Col)
Col1 = NewTag('Col1', 'div', Col, class_='grd-row-col-1-6')
Col2 = NewTag('Col2', 'div', Col, class_='grd-row-col-1-6')
Col3 = NewTag('Col3', 'div', Col, class_='grd-row-col-2-6')
Col4 = NewTag('Col4', 'div', Col, class_='grd-row-col-2-6')
Col5 = NewTag('Col5', 'div', Col, class_='grd-row-col-3-6')
Col6 = NewTag('Col6', 'div', Col, class_='grd-row-col-3-6')
Col7 = NewTag('Col7', 'div', Col, class_='grd-row-col-4-6')
Col8 = NewTag('Col8', 'div', Col, class_='grd-row-col-4-6')
Col9 = NewTag('Col9', 'div', Col, class_='grd-row-col-5-6')
Col10 = NewTag('Col10', 'div', Col, class_='grd-row-col-5-6')
Col11 = NewTag('Col11', 'div', Col, class_='grd-row-col-5-6')
Col12 = NewTag('Col12', 'div', Col)
