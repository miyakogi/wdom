#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from itertools import chain


from wdom import server_tornado
from wdom.misc import install_asyncio
from wdom.testing import TestCase, RemoteBrowserTestCase
from wdom.tests.remote_browser import test_node, test_tag


def setUpModule():
    install_asyncio()


test_cases = (
    case for case in chain(vars(test_node).values(), vars(test_tag).values())
    if isinstance(case, type) and
    issubclass(case, RemoteBrowserTestCase) and
    not issubclass(case, TestCase)
)
wait_time = 0.2 if os.environ.get('TRAVIS', False) else 0.05

for case in test_cases:
    name = 'Test' + case.__name__.replace('TestCase', 'AIO')
    globals()[name] = type(name, (case, TestCase), {
        'module': server_tornado,
        'wait_time': wait_time,
    })
