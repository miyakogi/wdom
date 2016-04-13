#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from wdom.testing import start_remote_browser, close_remote_browser


@pytest.fixture(scope='session', autouse=True)
def browser(request):
    start_remote_browser()
    request.addfinalizer(close_remote_browser)
