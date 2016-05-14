#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tag import H1

h1 = H1(class_='title')
print(h1.html_noid)  # <h1 class="title"></h1>

# this is equivalent to:
h1 = H1()
h1.setAttribute('class', 'title')
# also same as:
h1.classList.add('title')
# classList.add accepts mutliple arguments
h1.classList.add('title', 'heading', '...', )
