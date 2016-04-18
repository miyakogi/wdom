#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '//cdn.rawgit.com/alexanderGugel/papier/master/dist/papier-1.0.0.min.css',
]

DefaultButton = NewTag('DefaultButton', 'button', Button, class_='bg-white')
PrimaryButton = NewTag('PrimaryButton', 'button', Button, class_='bg-blue')
SuccessButton = NewTag('SuccessButton', 'button', Button, class_='bg-light-blue')
InfoButton = NewTag('InfoButton', 'button', Button, class_='bg-green')
WarningButton = NewTag('WarningButton', 'button', Button, class_='bg-orange')
DangerButton = NewTag('DangerButton', 'button', Button, class_='bg-red')
LinkButton = NewTag('LinkButton', 'button', Button, class_='bg-cyan')

Row = NewTag('Row', 'div', Row, class_='row')
Col1 = NewTag('Col1', 'div', Col, class_='col-1')
Col2 = NewTag('Col2', 'div', Col, class_='col-2')
Col3 = NewTag('Col3', 'div', Col, class_='col-3')
Col4 = NewTag('Col4', 'div', Col, class_='col-4')
Col5 = NewTag('Col5', 'div', Col, class_='col-5')
Col6 = NewTag('Col6', 'div', Col, class_='col-6')
Col7 = NewTag('Col7', 'div', Col, class_='col-7')
Col8 = NewTag('Col8', 'div', Col, class_='col-8')
Col9 = NewTag('Col9', 'div', Col, class_='col-9')
Col10 = NewTag('Col10', 'div', Col, class_='col-10')
Col11 = NewTag('Col11', 'div', Col, class_='col-11')
Col12 = NewTag('Col12', 'div', Col, class_='col-12')
