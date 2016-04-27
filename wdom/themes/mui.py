#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'MUI'
project_url = 'https://www.muicss.com/'
project_repository = 'https://github.com/muicss/mui'
license = 'MIT License'
license_url = 'https://github.com/muicss/mui/blob/master/LICENSE.txt'

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
DefaultButton = NewTag('DefaultButton', 'button', RaisedButton, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', RaisedButton, class_='mui-btn--primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', RaisedButton, class_='mui-btn--accent', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', RaisedButton, class_='mui-btn--accent', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', FlatButton, class_='mui-btn--accent', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='mui-btn--danger', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', WarningButton, class_='mui-btn--raised', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', WarningButton, class_='mui-btn--raised', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', FlatButton, class_='mui-btn--primary', is_='link-button')

Table = NewTag('Table', 'table', Table, class_='mui-table')

H1 = NewTag('H1', 'div', H1, class_='mui--text-display4')
H2 = NewTag('H2', 'div', H2, class_='mui--text-display3')
H3 = NewTag('H3', 'div', H3, class_='mui--text-display2')
H4 = NewTag('H4', 'div', H4, class_='mui--text-display1')
H5 = NewTag('H5', 'div', H5, class_='mui--text-headline')
H6 = NewTag('H6', 'div', H6, class_='mui--text-title')

Container = NewTag('Container', 'div', Container, class_='mui-container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='mui-container')
Row = NewTag('Row', 'div', Row, class_='mui-row')

Col1 = NewTag('Col1', 'div', Col1, class_='mui-col-xs-1 mui-col-sm-1 mui-col-md-1 mui-col-lg-1')
Col2 = NewTag('Col2', 'div', Col2, class_='mui-col-xs-2 mui-col-sm-2 mui-col-md-2 mui-col-lg-2')
Col3 = NewTag('Col3', 'div', Col3, class_='mui-col-xs-3 mui-col-sm-3 mui-col-md-3 mui-col-lg-3')
Col4 = NewTag('Col4', 'div', Col4, class_='mui-col-xs-4 mui-col-sm-4 mui-col-md-4 mui-col-lg-4')
Col5 = NewTag('Col5', 'div', Col5, class_='mui-col-xs-5 mui-col-sm-5 mui-col-md-5 mui-col-lg-5')
Col6 = NewTag('Col6', 'div', Col6, class_='mui-col-xs-6 mui-col-sm-6 mui-col-md-6 mui-col-lg-6')
Col7 = NewTag('Col7', 'div', Col7, class_='mui-col-xs-7 mui-col-sm-7 mui-col-md-7 mui-col-lg-7')
Col8 = NewTag('Col8', 'div', Col8, class_='mui-col-xs-8 mui-col-sm-8 mui-col-md-8 mui-col-lg-8')
Col9 = NewTag('Col9', 'div', Col9, class_='mui-col-xs-9 mui-col-sm-9 mui-col-md-9 mui-col-lg-9')
Col10 = NewTag('Col10', 'div', Col10, class_='mui-col-xs-10 mui-col-sm-10 mui-col-md-10 mui-col-lg-10')
Col11 = NewTag('Col11', 'div', Col11, class_='mui-col-xs-11 mui-col-sm-11 mui-col-md-11 mui-col-lg-11')

extended_classes = [
    Button,
    RaisedButton,
    FlatButton,
    DefaultButton,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    InfoButton,
    WarningButton,
    DangerButton,
    ErrorButton,
    LinkButton,
    Table,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
    Container,
    Wrapper,
    Row,
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
]
