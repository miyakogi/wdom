#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

css_files = [
    '//cdn.muicss.com/mui-0.5.1/css/mui.min.css',
]
js_files = [
    '//cdn.muicss.com/mui-0.5.1/js/mui.min.js',
]
headers = []

Button = NewTag('Button', bases=Button, class_='mui-btn')
RaisedButton = NewTag('RaisedButton', 'button', Button, class_='mui-btn--raised')
FlatButton = NewTag('FlatButton', 'button', Button, class_='mui-btn--flat')
DefaultButton = NewTag('DefaultButton', 'button', RaisedButton)
PrimaryButton = NewTag('PrimaryButton', 'button', RaisedButton, class_='mui-btn--primary')
SuccessButton = NewTag('SuccessButton', 'button', RaisedButton, class_='mui-btn--accent')
InfoButton = NewTag('InfoButton', 'button', FlatButton, class_='mui-btn--accent')
WarningButton = NewTag('WarningButton', 'button', Button, class_='mui-btn--danger')
DangerButton = NewTag('DangerButton', 'button', WarningButton, class_='mui-btn--raised')
LinkButton = NewTag('LinkButton', 'button', FlatButton, class_='mui-btn--primary')

Table = NewTag('Table', 'table', Table, class_='mui-table')

Container = NewTag('Container', 'div', class_='mui-container')
Wrapper = Container
Row = NewTag('Row', 'div', class_='mui-row')

H1 = NewTag('H1', 'div', H1, class_='mui--text-display4')
H2 = NewTag('H2', 'div', H2, class_='mui--text-display3')
H3 = NewTag('H3', 'div', H3, class_='mui--text-display2')
H4 = NewTag('H4', 'div', H4, class_='mui--text-display1')
H5 = NewTag('H5', 'div', H5, class_='mui--text-headline')
H6 = NewTag('H6', 'div', H6, class_='mui--text-title')
