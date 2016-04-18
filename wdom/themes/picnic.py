#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '//cdn.jsdelivr.net/picnicss/5.1.0/picnic.min.css',
]

Button = NewTag('Button', bases=Button)
DefaultButton = NewTag('DefaultButton', 'button', Button)
PrimaryButton = NewTag('PrimaryButton', 'button', Button)
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='success')
InfoButton = NewTag('InfoButton', 'button', Button)
WarningButton = NewTag('WarningButton', 'button', Button, class_='warning')
DangerButton = NewTag('DangerButton', 'button', Button, class_='error')
LinkButton = NewTag('LinkButton', 'button', Button, class_='pseudo')
