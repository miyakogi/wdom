#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://purecss.io/'
project_repository = 'https://github.com/yahoo/pure/'

css_files = [
    '//yui.yahooapis.com/pure/0.6.0/pure-min.css',
    '_static/css/pure-extra.css',
]

Button = NewTag('Button', bases=Button, class_='pure-button')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='pure-button-primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='pure-button-success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='pure-button-secondary')
WarningButton = NewTag('WarningButton', 'button', Button, class_='pure-button-warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='pure-button-error')
LinkButton = NewTag('LinkButton', 'button', Button, class_='pure-button-link')

Form = NewTag('Form', 'form', Form, class_='pure-form')

Table = NewTag('Table', 'table', Table, class_='pure-table')

Row = NewTag('Row', 'div', Row, class_='pure-g')
Col1 = NewTag('Col1', 'div', Col, class_='pure-u-2-24')
Col2 = NewTag('Col2', 'div', Col, class_='pure-u-4-24')
Col3 = NewTag('Col3', 'div', Col, class_='pure-u-6-24')
Col4 = NewTag('Col4', 'div', Col, class_='pure-u-8-24')
Col5 = NewTag('Col5', 'div', Col, class_='pure-u-10-24')
Col6 = NewTag('Col6', 'div', Col, class_='pure-u-12-24')
Col7 = NewTag('Col7', 'div', Col, class_='pure-u-14-24')
Col8 = NewTag('Col8', 'div', Col, class_='pure-u-16-24')
Col9 = NewTag('Col9', 'div', Col, class_='pure-u-18-24')
Col10 = NewTag('Col10', 'div', Col, class_='pure-u-20-24')
Col11 = NewTag('Col11', 'div', Col, class_='pure-u-22-24')
Col12 = NewTag('Col12', 'div', Col, class_='pure-u-24-24')
