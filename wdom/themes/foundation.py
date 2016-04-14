#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    'https://cdn.jsdelivr.net/foundation/6.2.1/foundation.min.css',
]

js_files = [
    'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js',
    'https://cdn.jsdelivr.net/foundation/6.2.1/foundation.min.js',
]

headers = []

Button = NewTag('Button', bases=Button, class_='button')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='hollow secondary')
PrimaryButton = NewTag('PrimaryButton', 'button', Button)
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success')
InfoButton = NewTag('InfoButton', 'button', Button, class_='success hollow')
WarningButton = NewTag('WarningButton', 'button', Button, class_='warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='alert')
LinkButton = NewTag('LinkButton', 'button', Button, class_='hollow')
