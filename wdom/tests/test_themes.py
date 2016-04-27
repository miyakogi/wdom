#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from wdom.themes import theme_list

@pytest.mark.parametrize('theme', theme_list)
def test_import_all(theme):
    exec('from wdom.themes import {}'.format(theme))
    # Fails `import theme as a` in py.test
    a = locals()[theme]
    assert 'name' in dir(a)
    assert 'project_url' in dir(a)
    assert 'project_repository' in dir(a)
    assert 'license' in dir(a)
    assert 'license_url' in dir(a)
    assert 'css_files' in dir(a)
    assert 'js_files' in dir(a)
    assert 'headers' in dir(a)
    assert 'extended_classes' in dir(a)
