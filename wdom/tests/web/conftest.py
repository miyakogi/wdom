#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path

import pytest

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(__file__)))))

from wdom.tests.web.remote_browser import start_browser, close_browser

@pytest.fixture(scope='session', autouse=True)
def browser(request):
    start_browser()
    request.addfinalizer(close_browser)
