#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

css_files = [
    'https://fonts.googleapis.com/icon?family=Material+Icons',
    'https://code.getmdl.io/1.1.3/material.indigo-pink.min.css',
]
js_files = [
    'https://code.getmdl.io/1.1.3/material.min.js',
]
headers = []

Button = NewTag('Button', bases=Button, class_='mdl-button mdl-js-button')
DefaultButton = NewTag('DefaultButton', 'button', Button,
                       class_='mdl-button--raised')
PrimaryButton = NewTag('PrimaryButton', 'button', DefaultButton,
                       class_='mdl-button--primary')
SuccessButton = NewTag('SuccessButton', 'button', DefaultButton,
                       class_='mdl-button--accent')
InfoButton = NewTag('InfoButton', 'button', Button,
                    class_='mdl-button--primary')
WarningButton = NewTag('WarningButton', 'button', Button)
DangerButton = NewTag('DangerButton', 'button', Button)
LinkButton = NewTag('LinkButton', 'button', Button,
                    class_='mdl-button--accent')

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
