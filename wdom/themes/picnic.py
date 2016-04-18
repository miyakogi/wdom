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

Row = NewTag('Row', 'div', Row, class_='row')
Col1 = NewTag('Col1', 'div', Col)
Col2 = NewTag('Col2', 'div', Col)
Col3 = NewTag('Col3', 'div', Col, class_='fourth')
Col4 = NewTag('Col4', 'div', Col, class_='third')
Col5 = NewTag('Col5', 'div', Col)
Col6 = NewTag('Col6', 'div', Col, class_='half')
Col7 = NewTag('Col7', 'div', Col)
Col8 = NewTag('Col8', 'div', Col, class_='two-third')
Col9 = NewTag('Col9', 'div', Col, class_='three-fourth')
Col10 = NewTag('Col10', 'div', Col)
Col11 = NewTag('Col11', 'div', Col)
Col12 = NewTag('Col12', 'div', Col)
