#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if sys.version_info < (3, 5):
    import warnings
    warnings.warn(
        'Next version of WDOM will not support python 3.4. Please update to version 3.6+.'  # noqa: E501
    )
