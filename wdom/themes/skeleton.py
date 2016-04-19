#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://getskeleton.com/'
project_repository = 'https://github.com/dhg/Skeleton'

css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css',
]

PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='button-primary')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='columns')
Col1 = NewTag('Col1', 'div', Col, class_='one column')
Col2 = NewTag('Col2', 'div', Col, class_='two')
Col3 = NewTag('Col3', 'div', Col, class_='three')
Col4 = NewTag('Col4', 'div', Col, class_='four')
Col5 = NewTag('Col5', 'div', Col, class_='five')
Col6 = NewTag('Col6', 'div', Col, class_='six')
Col7 = NewTag('Col7', 'div', Col, class_='seven')
Col8 = NewTag('Col8', 'div', Col, class_='eight')
Col9 = NewTag('Col9', 'div', Col, class_='nine')
Col10 = NewTag('Col10', 'div', Col, class_='ten')
Col11 = NewTag('Col11', 'div', Col, class_='eleven')
Col12 = NewTag('Col12', 'div', Col, class_='twelve')
