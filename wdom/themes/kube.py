#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import NewTagClass as NewTag
from wdom.tag import *


css_files = [
    '_static/css/kube.min.css',
]


class TypedButton(Button):
    type_ = None
    outline = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type_:
            self.setAttribute('type', self.type_)
        if self.outline:
            self.setAttribute('outline', True)

DefaultButton = NewTag('DefaultButton', 'button', TypedButton, type_='black',
                       outline=True)
PrimaryButton = NewTag('PrimaryButton', 'button', TypedButton, type_='primary')
SuccessButton = NewTag('SuccessButton', 'button', TypedButton, type_='black')
InfoButton = NewTag('InfoButton', 'button', TypedButton, type_='primary',
                    outline=True)
WarningButton = NewTag('WarningButton', 'button', TypedButton)
DangerButton = NewTag('DangerButton', 'button', TypedButton)
LinkButton = NewTag('LinkButton', 'button', TypedButton, outline=True)

Form = NewTag('Form', 'form', Form, class_='forms')
Select = NewTag('Select', 'select', Select, class_='select')

Row = NewTag('Row', 'row', Div)

class Column(Div):
    tag = 'column'
    cols = 1
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute('cols', str(self.cols))

Col1 = NewTag('Col1', 'column', Column)
Col2 = NewTag('Col2', 'column', Column, cols=2)
Col3 = NewTag('Col3', 'column', Column, cols=3)
Col4 = NewTag('Col4', 'column', Column, cols=4)
Col5 = NewTag('Col5', 'column', Column, cols=5)
Col6 = NewTag('Col6', 'column', Column, cols=6)
Col7 = NewTag('Col7', 'column', Column, cols=7)
Col8 = NewTag('Col8', 'column', Column, cols=8)
Col9 = NewTag('Col9', 'column', Column, cols=9)
Col10 = NewTag('Col10', 'column', Column, cols=10)
Col11 = NewTag('Col11', 'column', Column, cols=11)
