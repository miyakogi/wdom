#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import Button, NewTagClass

# Making new class easily
MyButton = NewTagClass('MyButton', 'button', Button, class_='btn')
DefaultButton = NewTagClass('DefaultButton', 'button', MyButton, class_='btn-default')

print(MyButton().html_noid)
print(DefaultButton().html_noid)
