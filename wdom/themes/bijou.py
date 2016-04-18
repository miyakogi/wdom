#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '_static/css/bijou.min.css',
]

Button = NewTag('Button', bases=Button, class_='button small')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='success')
WarningButton = NewTag('WarningButton', 'button', Button, class_='danger')
DangerButton = NewTag('DangerButton', 'button', Button, class_='danger')
LinkButton = NewTag('LinkButton', 'button', Button)

Table = NewTag('Table', 'table', Table, class_='table')
Row = NewTag('Row', 'div', class_='row')
Col1 = NewTag('Col', 'div', class_='span one')
Col2 = NewTag('Col', 'div', class_='span two')
Col3 = NewTag('Col', 'div', class_='span three')
Col4 = NewTag('Col', 'div', class_='span four')
Col5 = NewTag('Col', 'div', class_='span five')
Col6 = NewTag('Col', 'div', class_='span six')
Col7 = NewTag('Col', 'div', class_='span seven')
Col8 = NewTag('Col', 'div', class_='span eight')
Col9 = NewTag('Col', 'div', class_='span nine')
Col10 = NewTag('Col', 'div', class_='span ten')
Col11 = NewTag('Col', 'div', class_='span eleven')
