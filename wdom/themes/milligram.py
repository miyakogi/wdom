#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Milligram'
project_url = 'http://milligram.github.io/'
project_repository = 'https://github.com/milligram/milligram'
license = 'MIT License'
license_url = 'https://github.com/milligram/milligram/blob/master/license'

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

Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='column')
Col1 = NewTag('Col1', 'div', Col1, class_='column-10 column')
Col2 = NewTag('Col2', 'div', Col2, class_='column-20 column')
Col3 = NewTag('Col3', 'div', Col3, class_='column-25 column')
Col4 = NewTag('Col4', 'div', Col4, class_='column-33 column')
Col5 = NewTag('Col5', 'div', Col5, class_='column-41 column')
Col6 = NewTag('Col6', 'div', Col6, class_='column-50 column')
Col7 = NewTag('Col7', 'div', Col7, class_='column-60 column')
Col8 = NewTag('Col8', 'div', Col8, class_='column-67 column')
Col9 = NewTag('Col9', 'div', Col9, class_='column-75 column')
Col10 = NewTag('Col10', 'div', Col10, class_='column-80 column')
Col11 = NewTag('Col11', 'div', Col11, class_='column-90 column')
Col12 = NewTag('Col12', 'div', Col12, class_='column-100 column')

extended_classes = [
    DefaultButton,
    InfoButton,
    PrimaryButton,
    LinkButton,
    Button,
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
