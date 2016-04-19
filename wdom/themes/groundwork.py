#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'https://groundworkcss.github.io/groundwork/'
project_repository = 'https://github.com/groundworkcss/groundwork'

css_files = [
    '_static/css/groundwork.css',
]

js_files = [
    '//cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js',
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '_static/js/groundwork.all.js',
]

Button = NewTag('Button', bases=Button)
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='blue')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='info')
WarningButton = NewTag('WarningButton', 'button', Button, class_='warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='error')
LinkButton = NewTag('LinkButton', 'button', Button, class_='green')

Row = NewTag('Row', 'div', Row, class_='row')
Col1 = NewTag('Col1', 'div', Col, class_='one twelfth')
Col2 = NewTag('Col2', 'div', Col, class_='one sixth')
Col3 = NewTag('Col3', 'div', Col, class_='one fourth')
Col4 = NewTag('Col4', 'div', Col, class_='one third')
Col5 = NewTag('Col5', 'div', Col, class_='five twelfths')
Col6 = NewTag('Col6', 'div', Col, class_='one half')
Col7 = NewTag('Col7', 'div', Col, class_='seven twelfths')
Col8 = NewTag('Col8', 'div', Col, class_='two thirds')
Col9 = NewTag('Col9', 'div', Col, class_='three fourths')
Col10 = NewTag('Col10', 'div', Col, class_='five sixths')
Col11 = NewTag('Col11', 'div', Col, class_='eleven twelfths')
Col12 = NewTag('Col12', 'div', Col)
