#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import logging

__all__ = ('logger', 'theme_list')

logger = logging.getLogger(__name__)
curdir = os.path.dirname(os.path.abspath(__file__))
theme_list = sorted(set(re.sub(r'\.py[codx]?$', '', file)
                        for file in os.listdir(curdir)
                        if not file.startswith('_')))
