#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '//cdnjs.cloudflare.com/ajax/libs/furtive/2.2.3/furtive.css',
]

Button = NewTag('Button', 'a', Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'a', Button)
PrimaryButton = NewTag('PrimaryButton', 'a', Button, class_='btn--blue')
SuccessButton = NewTag('SuccessButton', 'a', Button, class_='btn--green')
InfoButton = NewTag('InfoButton', 'a', Button, class_='btn--blue')
WarningButton = NewTag('WarningButton', 'a', Button, class_='btn--red')
DangerButton = NewTag('DangerButton', 'a', Button, class_='btn--red')
LinkButton = NewTag('LinkButton', 'a', Button, class_='btn--link')

