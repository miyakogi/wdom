#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import pytest

from wdom.testing import start_webdriver, close_webdriver
from wdom import testing

orig_wait = testing.browser_implict_wait


@pytest.fixture(scope='session', autouse=True)
def browser(request):
    testing.browser_implict_wait = 1 if os.environ.get('TRAVIS') else 0.1
    start_webdriver()
    request.addfinalizer(close_webdriver)
    testing.browser_implict_wait = orig_wait
