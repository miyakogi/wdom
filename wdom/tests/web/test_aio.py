#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom import aioserver
from wdom.misc import install_asyncio
from wdom.tests.util import TestCase
from wdom.tests.web.test_web_node import WebElementTestCase, EventTestCase
from wdom.tests.web.test_tag_web import NodeTestCase, InputTestCase


def setup_module():
    install_asyncio()


class TestWebElementAIO(WebElementTestCase, TestCase):
    module = aioserver
    wait_time = 0.02


class TestEventAIO(EventTestCase, TestCase):
    module = aioserver
    wait_time = 0.02


class TestNodeAIO(NodeTestCase, TestCase):
    module = aioserver
    wait_time = 0.02


class TestInputAIO(InputTestCase, TestCase):
    module = aioserver
    wait_time = 0.02
