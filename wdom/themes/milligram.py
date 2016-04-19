#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://milligram.github.io/'
project_repository = 'https://github.com/milligram/milligram'

css_files = [
    '//fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic',
    '//cdnjs.cloudflare.com/ajax/libs/normalize/3.0.3/normalize.css',
    '//cdnjs.cloudflare.com/ajax/libs/milligram/1.1.0/milligram.min.css'
]

DefaultButton = NewTag('DefaultButton', 'button', Button, class_='button-outline')
InfoButton = NewTag('InfoButton', 'button', Button, class_='button-outline')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='button-primary')
LinkButton = NewTag('LinkButton', 'button', Button, class_='button-clear')
Button = NewTag('Button', 'button', DefaultButton, class_='button-outline')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='row')
Col = NewTag('Col', 'div', class_='column')
Col1 = NewTag('Col1', 'div', Col, class_='column-10')
Col2 = NewTag('Col2', 'div', Col, class_='column-20')
Col3 = NewTag('Col3', 'div', Col, class_='column-25')
Col4 = NewTag('Col4', 'div', Col, class_='column-33')
Col5 = NewTag('Col5', 'div', Col, class_='column-41')
Col6 = NewTag('Col6', 'div', Col, class_='column-50')
Col7 = NewTag('Col7', 'div', Col, class_='column-60')
Col8 = NewTag('Col8', 'div', Col, class_='column-67')
Col9 = NewTag('Col9', 'div', Col, class_='column-75')
Col10 = NewTag('Col10', 'div', Col, class_='column-80')
Col11 = NewTag('Col11', 'div', Col, class_='column-90')
Col12 = NewTag('Col12', 'div', Col, class_='column-100')
