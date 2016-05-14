#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Material Design Lite (MDL)'
project_url = 'http://www.getmdl.io/'
project_repository = 'https://github.com/google/material-design-lite'
license = 'Apache License 2.0'
license_url = 'https://github.com/google/material-design-lite/blob/master/LICENSE'

css_files = [
    '//fonts.googleapis.com/icon?family=Material+Icons',
    '//code.getmdl.io/1.1.3/material.indigo-pink.min.css',
]
js_files = [
    '//code.getmdl.io/1.1.3/material.min.js',
]
headers = []

Button = NewTag('Button', bases=Button, class_='mdl-button mdl-js-button')
DefaultButton = NewTag('DefaultButton', 'button', Button,
                       class_='mdl-button--raised', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', DefaultButton,
                       class_='mdl-button--primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button,
                         class_='mdl-button--raised', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', DefaultButton,
                       class_='mdl-button--accent', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button,
                    class_='mdl-button--primary', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button,
                    class_='mdl-button--accent', is_='link-button')

FormGroup = NewTag('FormGroup', 'div', Div, class_='mdl-textfield mdl-js-textfield')
Input = NewTag('Input', 'input', Input, class_='mdl-textfield__input')
Label = NewTag('Label', 'label', Label, class_='mdl-textfield__label')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='mdl-textfield__input')
Select = NewTag('Select', 'select', Select, class_='mdl-textfield__input')

Table = NewTag('Table', 'table', Table, class_='mdl-data-table mdl-js-data-table')
Th = NewTag('Th', 'th', Th, class_='mdl-data-table__cell--non-numeric')
Td = NewTag('Td', 'td', Td, class_='mdl-data-table__cell--non-numeric')

H1 = NewTag('H1', 'div', H1, class_='mdl-typography--display-4')
H2 = NewTag('H2', 'div', H2, class_='mdl-typography--display-3')
H3 = NewTag('H3', 'div', H3, class_='mdl-typography--display-2')
H4 = NewTag('H4', 'div', H4, class_='mdl-typography--display-1')
H5 = NewTag('H5', 'div', H5, class_='mdl-typography--headline')
H6 = NewTag('H6', 'div', H6, class_='mdl-typography--title')

Row = NewTag('Row', 'div', Row, class_='mdl-grid')
Col = NewTag('Col', 'div', Col, class_='mdl-cell')
Col1 = NewTag('Col1', 'div', Col1, class_='mdl-cell mdl-cell--1-col')
Col2 = NewTag('Col2', 'div', Col2, class_='mdl-cell mdl-cell--2-col')
Col3 = NewTag('Col3', 'div', Col3, class_='mdl-cell mdl-cell--3-col')
Col4 = NewTag('Col4', 'div', Col4, class_='mdl-cell mdl-cell--4-col')
Col5 = NewTag('Col5', 'div', Col5, class_='mdl-cell mdl-cell--5-col')
Col6 = NewTag('Col6', 'div', Col6, class_='mdl-cell mdl-cell--6-col')
Col7 = NewTag('Col7', 'div', Col7, class_='mdl-cell mdl-cell--7-col')
Col8 = NewTag('Col8', 'div', Col8, class_='mdl-cell mdl-cell--8-col')
Col9 = NewTag('Col9', 'div', Col9, class_='mdl-cell mdl-cell--9-col')
Col10 = NewTag('Col10', 'div', Col10, class_='mdl-cell mdl-cell--10-col')
Col11 = NewTag('Col11', 'div', Col11, class_='mdl-cell mdl-cell--11-col')
Col12 = NewTag('Col12', 'div', Col12, class_='mdl-cell mdl-cell--12-col')

extended_classes = [
    Button,
    DefaultButton,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    InfoButton,
    WarningButton,
    DangerButton,
    ErrorButton,
    LinkButton,
    FormGroup,
    Input,
    Label,
    Textarea,
    Select,
    Table,
    Th,
    Td,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
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
