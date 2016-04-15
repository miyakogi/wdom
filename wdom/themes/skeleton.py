#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css',
]

PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='button-primary')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='row')
Col1 = NewTag('Col', 'div', class_='one column')
Col2 = NewTag('Col', 'div', class_='two columns')
Col3 = NewTag('Col', 'div', class_='three columns')
Col4 = NewTag('Col', 'div', class_='four columns')
Col5 = NewTag('Col', 'div', class_='five columns')
Col6 = NewTag('Col', 'div', class_='six columns')
Col7 = NewTag('Col', 'div', class_='seven columns')
Col8 = NewTag('Col', 'div', class_='eight columns')
Col9 = NewTag('Col', 'div', class_='nine columns')
Col10 = NewTag('Col', 'div', class_='ten columns')
Col11 = NewTag('Col', 'div', class_='eleven columns')
