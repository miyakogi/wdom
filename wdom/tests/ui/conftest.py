#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from wdom.tests.ui.wd import start_wd, close_wd


@pytest.fixture(scope='session', autouse=True)
def browser(request):
    start_wd()
    request.addfinalizer(close_wd)
