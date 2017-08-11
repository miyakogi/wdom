#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa

from wdom.tag import NewTagClass as NewTag
from wdom.themes import *

name = 'Vital'
project_url = 'https://vitalcss.com/'
project_repository = 'https://github.com/doximity/vital'
license = 'Apache 2.0'
license_url = 'https://github.com/doximity/vital/blob/master/LICENSE.md'

css_files = [
    '//cdn.rawgit.com/doximity/vital/v2.2.1/dist/css/vital.min.css',
]

Button = NewTag('Button', bases=Button, class_='btn')
DefaultButton = NewTag('DefaultButton', 'button', Button, class_='solid', is_='default-button')
PrimaryButton = NewTag('PrimaryButton', 'button', DefaultButton, class_='blue', is_='primary-button')
SecondaryButton = NewTag('SecondaryButton', 'button', Button, class_='blue', is_='secondary-button')
SuccessButton = NewTag('SuccessButton', 'button', DefaultButton, class_='green', is_='success-button')
InfoButton = NewTag('InfoButton', 'button', Button, class_='blue', is_='info-button')
WarningButton = NewTag('WarningButton', 'button', DefaultButton, class_='orange', is_='warning-button')
DangerButton = NewTag('DangerButton', 'button', DefaultButton, class_='red', is_='danger-button')
ErrorButton = NewTag('ErrorButton', 'button', DefaultButton, class_='red', is_='error-button')
LinkButton = NewTag('LinkButton', 'button', Button, class_='no-outline blue', is_='link-button')

Ol = NewTag('Ol', 'ol', class_='list')
Ul = NewTag('Ul', 'Ul', class_='list')

Col = NewTag('Col', 'div', Col, class_='col')
# Col1 = NewTag('Col1', 'div', Col1, class_='col-1-12')
# Col2 = NewTag('Col2', 'div', Col2, class_='col-1-6')
Col3 = NewTag('Col3', 'div', Col3, class_='col-1-4')
Col4 = NewTag('Col4', 'div', Col4, class_='col-1-3')
# Col5 = NewTag('Col5', 'div', Col5, class_='col-5-12')
Col6 = NewTag('Col6', 'div', Col6, class_='col-1-2')
# Col7 = NewTag('Col7', 'div', Col7, class_='col-7-12')
Col8 = NewTag('Col8', 'div', Col8, class_='col-2-3')
Col9 = NewTag('Col9', 'div', Col9, class_='col-3-4')
# Col10 = NewTag('Col10', 'div', Col10, class_='col-5-6')
# Col11 = NewTag('Col11', 'div', Col11, class_='col-11-12')
# Col12 = NewTag('Col12', 'div', Col12, class_='col-1-1')
