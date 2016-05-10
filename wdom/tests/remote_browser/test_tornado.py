#!/usr/bin/env py.test
# -*- coding: utf-8 -*-

import os
from itertools import chain

from wdom.misc import install_asyncio
from wdom.testing import TestCase, RemoteBrowserTestCase
from wdom.tests.remote_browser import test_node, test_tag
from wdom.testing import start_remote_browser, close_remote_browser


def setUpModule():
    install_asyncio()
    start_remote_browser()


def tearDownModule():
    close_remote_browser()


test_cases = (
    case for case in chain(vars(test_node).values(), vars(test_tag).values())
    if isinstance(case, type) and
    issubclass(case, RemoteBrowserTestCase) and
    not issubclass(case, TestCase)
)
wait_time = 0.2 if os.environ.get('TRAVIS', False) else 0.05

for case in test_cases:
    name = 'Test' + case.__name__.replace('TestCase', 'Tornado')
    globals()[name] = type(name, (case, TestCase), {
        'server_type': 'tornado',
        'wait_time': wait_time,
    })
