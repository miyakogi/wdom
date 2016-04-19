#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://codewithspark.com/'
project_repository = 'https://github.com/twistedpixel/spark/'

css_files = [
    '_static/css/spark.min.css',
]

js_files = [
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '_static/js/spark.min.js',
]

headers = []

Button = NewTag('Button', bases=Button, class_='btn flat')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='black')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='blue')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='lime')
InfoButton = NewTag('InfoButton', 'button', Button, class_='green')
WarningButton = NewTag('WarningButton', 'button', Button, class_='orange')
DangerButton = NewTag('DangerButton', 'button', Button, class_='red')
LinkButton = NewTag('LinkButton', 'button', Button, class_='flat')

class Form(Form):
    class_ = 'form'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('role', 'form')

Table = NewTag('Table', 'table', Table, class_='tbl')

Container = NewTag('Container', 'div', class_='container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='row')
Col = NewTag('Col', 'div', class_='col')
Col1 = NewTag('Col1', 'div', Col, class_='of-1')
Col2 = NewTag('Col2', 'div', Col, class_='of-2')
Col3 = NewTag('Col3', 'div', Col, class_='of-3')
Col4 = NewTag('Col4', 'div', Col, class_='of-4')
Col5 = NewTag('Col5', 'div', Col, class_='of-5')
Col6 = NewTag('Col6', 'div', Col, class_='of-6')
Col7 = NewTag('Col7', 'div', Col, class_='of-7')
Col8 = NewTag('Col8', 'div', Col, class_='of-8')
Col9 = NewTag('Col9', 'div', Col, class_='of-9')
Col10 = NewTag('Col10', 'div', Col, class_='of-10')
Col11 = NewTag('Col11', 'div', Col, class_='of-11')
Col12 = NewTag('Col12', 'div', Col, class_='of-12')
