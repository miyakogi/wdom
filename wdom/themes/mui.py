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

Col1 = NewTag('Col', 'div', class_='mui-col-xs-1 mui-col-sm-1 mui-col-md-1 mui-col-lg-1')
Col2 = NewTag('Col', 'div', class_='mui-col-xs-2 mui-col-sm-2 mui-col-md-2 mui-col-lg-2')
Col3 = NewTag('Col', 'div', class_='mui-col-xs-3 mui-col-sm-3 mui-col-md-3 mui-col-lg-3')
Col4 = NewTag('Col', 'div', class_='mui-col-xs-4 mui-col-sm-4 mui-col-md-4 mui-col-lg-4')
Col5 = NewTag('Col', 'div', class_='mui-col-xs-5 mui-col-sm-5 mui-col-md-5 mui-col-lg-5')
Col6 = NewTag('Col', 'div', class_='mui-col-xs-6 mui-col-sm-6 mui-col-md-6 mui-col-lg-6')
Col7 = NewTag('Col', 'div', class_='mui-col-xs-7 mui-col-sm-7 mui-col-md-7 mui-col-lg-7')
Col8 = NewTag('Col', 'div', class_='mui-col-xs-8 mui-col-sm-8 mui-col-md-8 mui-col-lg-8')
Col9 = NewTag('Col', 'div', class_='mui-col-xs-9 mui-col-sm-9 mui-col-md-9 mui-col-lg-9')
Col10 = NewTag('Col', 'div', class_='mui-col-xs-10 mui-col-sm-10 mui-col-md-10 mui-col-lg-10')
Col11 = NewTag('Col', 'div', class_='mui-col-xs-11 mui-col-sm-11 mui-col-md-11 mui-col-lg-11')

H1 = NewTag('H1', 'div', H1, class_='mui--text-display4')
H2 = NewTag('H2', 'div', H2, class_='mui--text-display3')
H3 = NewTag('H3', 'div', H3, class_='mui--text-display2')
H4 = NewTag('H4', 'div', H4, class_='mui--text-display1')
H5 = NewTag('H5', 'div', H5, class_='mui--text-headline')
H6 = NewTag('H6', 'div', H6, class_='mui--text-title')
