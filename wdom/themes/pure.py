#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    'http://yui.yahooapis.com/pure/0.6.0/pure-min.css',
    '_static/css/pure-extra.css',
]

Button = NewTag('Button', bases=Button, class_='pure-button')
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='pure-button-primary')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='pure-button-success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='pure-button-secondary')
WarningButton = NewTag('WarningButton', 'button', Button, class_='pure-button-warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='pure-button-error')
LinkButton = NewTag('LinkButton', 'button', Button, class_='pure-button-link')

Form = NewTag('Form', 'form', Form, class_='pure-form')

Table = NewTag('Table', 'table', Table, class_='pure-table')
