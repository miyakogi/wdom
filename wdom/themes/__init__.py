#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa

import os
import re
import logging

from wdom.tag import *

logger = logging.getLogger(__name__)
curdir = os.path.dirname(os.path.abspath(__file__))
theme_list = sorted(set(re.sub(r'\.py[codx]?$', '', file)
                        for file in os.listdir(curdir)
                        if not file.startswith('_')))

# theme informations
name = 'default'
project_url = ''
project_repository = ''
license = ''
license_url = ''

# css/js/headers
css_files = []  # type: List[str]
js_files = []  # type: List[str]
headers = []  # type: List[str]

TextInput = NewTagClass('TextInput', 'input', Input, type_='text')
CheckBox = NewTagClass('CheckBox', 'input', Input, type_='checkbox')
RadioButton = NewTagClass('RadioButton', 'input', Input, type_='radio')

# Building blocks
Container = NewTagClass('Container', 'div', Div, is_='container')
Wrapper = NewTagClass('Wrapper', 'div', Div, is_='wrapper')
Row = NewTagClass('Row', 'div', Div, is_='row')
FormGroup = NewTagClass('FormGroup', 'div', Div, is_='formgroup')
FormOuter = NewTagClass('FormOuter', 'div', Div, is_='form-outer')
FormInner = NewTagClass('FormInner', 'div', Div, is_='form-inner')
FormItem = NewTagClass('FormItem', 'div', Div, is_='form-item')
Col = NewTagClass('Col', 'div', Div, is_='col')
Col1 = NewTagClass('Col1', 'div', Div, is_='col1')
Col2 = NewTagClass('Col2', 'div', Div, is_='col2')
Col3 = NewTagClass('Col3', 'div', Div, is_='col3')
Col4 = NewTagClass('Col4', 'div', Div, is_='col4')
Col5 = NewTagClass('Col5', 'div', Div, is_='col5')
Col6 = NewTagClass('Col6', 'div', Div, is_='col6')
Col7 = NewTagClass('Col7', 'div', Div, is_='col7')
Col8 = NewTagClass('Col8', 'div', Div, is_='col8')
Col9 = NewTagClass('Col9', 'div', Div, is_='col9')
Col10 = NewTagClass('Col10', 'div', Div, is_='col10')
Col11 = NewTagClass('Col11', 'div', Div, is_='col11')
Col12 = NewTagClass('Col12', 'div', Div, is_='col12')

# Some css updates
DefaultButton = NewTagClass('DefaultButton', 'button', Button, is_='default-button')
PrimaryButton = NewTagClass('PrimaryButton', 'button', Button, is_='primary-button')
SecondaryButton = NewTagClass('SecondaryButton', 'button', Button, is_='secondary-button')
SuccessButton = NewTagClass('SuccessButton', 'button', Button, is_='success-button')
InfoButton = NewTagClass('InfoButton', 'button', Button, is_='info-button')
WarningButton = NewTagClass('WarningButton', 'button', Button, is_='warning-button')
DangerButton = NewTagClass('DangerButton', 'button', Button, is_='danger-button')
ErrorButton = NewTagClass('ErrorButton', 'button', Button, is_='error-button')
LinkButton = NewTagClass('LinkButton', 'button', Button, is_='link-button')

extended_classes = [
    Container,
    Wrapper,
    Row,
    FormGroup,
    FormOuter,
    FormInner,
    FormItem,
    Col,
    Col1,
    Col2,
    Col3,
    Col4,
    Col5,
    Col6,
    Col7,
    Col8,
    Col9,
    Col10,
    Col11,
    Col12,
    DefaultButton,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    InfoButton,
    WarningButton,
    DangerButton,
    ErrorButton,
    LinkButton,
]
