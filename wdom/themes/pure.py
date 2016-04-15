#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    'http://yui.yahooapis.com/pure/0.6.0/pure-min.css',
]

Button = NewTag('Button', bases=Button, class_='pure-button')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='pure-button-primary')
SuccessButton = NewTag('SuccessButton', 'button', Button)
InfoButton = NewTag('InfoButton', 'button', Button)
WarningButton = NewTag('WarningButton', 'button', Button)
DangerButton = NewTag('DangerButton', 'button', Button)
ErrorButton = NewTag('ErrorButton', 'button', Button)
LinkButton = NewTag('LinkButton', 'button', Button)

Form = NewTag('Form', 'form', Form, class_='pure-form')

Table = NewTag('Table', 'table', Table, class_='pure-table')
