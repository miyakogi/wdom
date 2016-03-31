#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom import server_tornado
from wdom.misc import install_asyncio
from wdom.tests.util import TestCase
from wdom.tests.web.test_web_node import WebElementTestCase, EventTestCase
from wdom.tests.web.test_tag_web import NodeTestCase, InputTestCase


def setUpModule():
    install_asyncio()


test_cases = (WebElementTestCase, EventTestCase, NodeTestCase, InputTestCase)

for case in test_cases:
    name = 'Test' + case.__name__.replace('TestCase', 'AIO')
    globals()[name] = type(name, (case, TestCase), {
        'module': server_tornado,
        'wait_time': 0.05,
    })
