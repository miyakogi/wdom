#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from wdom import server_tornado
from wdom.misc import install_asyncio
from wdom.testing import TestCase
from wdom.tests.remote_browser.test_node import WebElementTestCase, EventTestCase
from wdom.tests.remote_browser.test_tag import NodeTestCase, InputTestCase


def setUpModule():
    install_asyncio()


test_cases = (WebElementTestCase, EventTestCase, NodeTestCase, InputTestCase)
wait_time = 0.2 if os.environ.get('TRAVIS', False) else 0.05

for case in test_cases:
    name = 'Test' + case.__name__.replace('TestCase', 'AIO')
    globals()[name] = type(name, (case, TestCase), {
        'module': server_tornado,
        'wait_time': wait_time,
    })
