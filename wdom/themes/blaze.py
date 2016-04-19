#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *

project_url = 'http://blazecss.com/'
project_repository = 'https://github.com/BlazeCSS/blaze'

css_files = [
    '//cdn.jsdelivr.net/blazecss/latest/blaze.min.css',
]

Button = NewTag('Button', bases=Button, class_='button')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='button--default')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='button--primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='button--success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='button--primary')
WarningButton = NewTag('WarningButton', 'button', Button, class_='button--secondary')
DangerButton = NewTag('DangerButton', 'button', Button, class_='button--error')
LinkButton = NewTag('LinkButton', 'button', Button)

Input = NewTag('Input', 'input', Input, class_='field')
TextInput = NewTag('TextInput', 'input', TextInput, class_='field')
Textarea = NewTag('Textarea', 'textarea', Textarea, class_='field')
Select = NewTag('Select', 'select', Select, class_='choice')

Ul = NewTag('Ul', 'ul', Ul, class_='list')
Ol = NewTag('Ol', 'ol', Ol, class_='list--ordered')
Li = NewTag('Li', 'li', Li, class_='list__item')

Table = NewTag('Table', 'table', Table, class_='table')
Tr = NewTag('Tr', 'tr', Tr, class_='table__row')
Th = NewTag('Th', 'th', Th, class_='table__cell')
Td = NewTag('Td', 'td', Td, class_='table__cell')

H1 = NewTag('H1', 'div', H1, class_='heading heading--super')
H2 = NewTag('H2', 'div', H2, class_='heading heading--xlarge')
H3 = NewTag('H3', 'div', H3, class_='heading heading--large')
H4 = NewTag('H4', 'div', H4, class_='heading heading--medium')
H5 = NewTag('H5', 'div', H5, class_='heading heading--small')
H6 = NewTag('H6', 'div', H6, class_='heading heading--xsmall')

Row = NewTag('Row', 'div', Row, class_='gird')
Col = NewTag('Col', 'div', Col, class_='grid__cell')
Col1 = NewTag('Col', 'div', Col, class_='grid__cell--width-8')
Col2 = NewTag('Col', 'div', Col, class_='grid__cell--width-17')
Col3 = NewTag('Col', 'div', Col, class_='grid__cell--width-25')
Col4 = NewTag('Col', 'div', Col, class_='grid__cell--width-33')
Col5 = NewTag('Col', 'div', Col, class_='grid__cell--width-42')
Col6 = NewTag('Col', 'div', Col, class_='grid__cell--width-50')
Col7 = NewTag('Col', 'div', Col, class_='grid__cell--width-58')
Col8 = NewTag('Col', 'div', Col, class_='grid__cell--width-67')
Col9 = NewTag('Col', 'div', Col, class_='grid__cell--width-75')
Col10 = NewTag('Col', 'div', Col, class_='grid__cell--width-83')
Col11 = NewTag('Col', 'div', Col, class_='grid__cell--width-92')
