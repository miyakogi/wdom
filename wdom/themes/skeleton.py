#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Skeleton'
project_url = 'http://getskeleton.com/'
project_repository = 'https://github.com/dhg/Skeleton'
license = 'MIT License'
license_url = 'https://github.com/dhg/Skeleton/blob/master/LICENSE.md'

css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css',
]

PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='button-primary', is_='primary-button')
Container = NewTag('Container', 'div', Container, class_='container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='container')
Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='columns')
Col1 = NewTag('Col1', 'div', Col1, class_='one column')
Col2 = NewTag('Col2', 'div', Col2, class_='two columns')
Col3 = NewTag('Col3', 'div', Col3, class_='three columns')
Col4 = NewTag('Col4', 'div', Col4, class_='four columns')
Col5 = NewTag('Col5', 'div', Col5, class_='five columns')
Col6 = NewTag('Col6', 'div', Col6, class_='six columns')
Col7 = NewTag('Col7', 'div', Col7, class_='seven columns')
Col8 = NewTag('Col8', 'div', Col8, class_='eight columns')
Col9 = NewTag('Col9', 'div', Col9, class_='nine columns')
Col10 = NewTag('Col10', 'div', Col10, class_='ten columns')
Col11 = NewTag('Col11', 'div', Col11, class_='eleven columns')
Col12 = NewTag('Col12', 'div', Col12, class_='twelve columns')

extended_classes = [
    PrimaryButton,
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
