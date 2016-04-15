#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.1.8/semantic.min.css',
]

# Need jQuery
js_files = [
    'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.1.8/semantic.min.js',
]

headers = []


# Buttons http://semantic-ui.com/elements/button.html
Button = NewTag('Button', bases=Button, class_='ui button')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='teal')
InfoButton = NewTag('InfoButton', 'button', Button, class_='green')
WarningButton = NewTag('WarningButton', 'button', Button, class_='orange')
DangerButton = NewTag('DangerButton', 'button', Button, class_='red')
LinkButton = NewTag('LinkButton', 'button', Button, class_='basic')

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
Container = NewTag('Container', 'div', class_='ui grid container')
Wrapper = Container
Row = NewTag('Row', 'div', Div, class_='row')
Col1 = NewTag('Col', 'div', Div, class_='column')
Col2 = NewTag('Col', 'div', Div, class_='two wide column')
Col3 = NewTag('Col', 'div', Div, class_='three wide column')
Col4 = NewTag('Col', 'div', Div, class_='four wide column')
Col5 = NewTag('Col', 'div', Div, class_='five wide column')
Col6 = NewTag('Col', 'div', Div, class_='six wide column')
Col7 = NewTag('Col', 'div', Div, class_='seven wide column')
Col8 = NewTag('Col', 'div', Div, class_='eight wide column')
Col9 = NewTag('Col', 'div', Div, class_='nine wide column')
Col10 = NewTag('Col', 'div', Div, class_='ten wide column')
Col11 = NewTag('Col', 'div', Div, class_='eleven wide column')
