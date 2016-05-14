#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

name = 'Semantic UI (Semantic)'
project_url = 'http://semantic-ui.com/'
project_repository = 'https://github.com/semantic-org/semantic-ui/'
license = 'MIT License'
license_url = 'https://github.com/Semantic-Org/Semantic-UI/blob/master/LICENSE.md'

css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.1.8/semantic.min.css',
]

# Need jQuery
js_files = [
    '//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    '//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.1.8/semantic.min.js',
]

headers = []

# Buttons http://semantic-ui.com/elements/button.html
Button = NewTag('Button', bases=Button, class_='ui button')
DefaultButton = NewTag('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='primary', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='blue', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='teal', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='green', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', Button, class_='orange', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', Button, class_='red', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', Button, class_='red', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='basic', is_='link-button')

# Form http://semantic-ui.com/collections/form.html
Form = NewTag('Form', 'form', Form, class_='ui form')
# DropDown http://semantic-ui.com/modules/dropdown.html
# document is not correct...
# Select = NewTag('Select', 'select', Select, class_='ui fluid dropdown')
Select = NewTag('Select', 'select', Select, class_='ui dropdown')

# List http://semantic-ui.com/elements/list.html
# Nested list with ul.list fails...
Ul = NewTag('Ul', 'div', Div, class_='ui bulleted list')
Li = NewTag('Li', 'div', Div, class_='item')
Ol = NewTag('Ol', 'div', Div, class_='ui ordered list')

# Table http://semantic-ui.com/collections/table.html
Table = NewTag('Table', 'table', Table, class_='ui celled table')

# Divider
Hr = NewTag('Hr', 'div', Div, class_='ui divider')

# Typography http://semantic-ui.com/elements/header.html
H1 = NewTag('H1', 'h1', H1, class_='ui header')
H2 = NewTag('H2', 'h2', H2, class_='ui header')
H3 = NewTag('H3', 'h3', H3, class_='ui header')
H4 = NewTag('H4', 'h4', H4, class_='ui header')
H5 = NewTag('H5', 'h5', H5, class_='ui header')
H6 = NewTag('H6', 'h6', H6, class_='ui header')

# Grid http://semantic-ui.com/collections/grid.html
# Too complicatted...
Container = NewTag('Container', 'div', Container, class_='ui grid container')
Wrapper = NewTag('Wrapper', 'div', Wrapper, class_='ui grid container')
Row = NewTag('Row', 'div', Row, class_='row')
Col = NewTag('Col', 'div', Col, class_='column')
Col1 = NewTag('Col1', 'div', Col1, class_='column')
Col2 = NewTag('Col2', 'div', Col2, class_='two wide column')
Col3 = NewTag('Col3', 'div', Col3, class_='three wide column')
Col4 = NewTag('Col4', 'div', Col4, class_='four wide column')
Col5 = NewTag('Col5', 'div', Col5, class_='five wide column')
Col6 = NewTag('Col6', 'div', Col6, class_='six wide column')
Col7 = NewTag('Col7', 'div', Col7, class_='seven wide column')
Col8 = NewTag('Col8', 'div', Col8, class_='eight wide column')
Col9 = NewTag('Col9', 'div', Col9, class_='nine wide column')
Col10 = NewTag('Col10', 'div', Col10, class_='ten wide column')
Col11 = NewTag('Col11', 'div', Col11, class_='eleven wide column')
Col12 = NewTag('Col12', 'div', Col12, class_='')

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
    Form,
    Select,
    Ul,
    Li,
    Ol,
    Table,
    Hr,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
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
