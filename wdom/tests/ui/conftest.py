#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from wdom.testing import start_webdriver, close_webdriver


@pytest.fixture(scope='session', autouse=True)
def browser(request):
    start_webdriver()
    request.addfinalizer(close_webdriver)
