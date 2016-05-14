#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib

from nose_parameterized import parameterized

from wdom.themes import theme_list
from wdom.testing import TestCase


class TestThemesImport(TestCase):
    @parameterized.expand(theme_list)
    def test_import_all(self, theme):
        a = importlib.import_module('wdom.themes.' + theme)
        self.assertIn('name', dir(a))
        self.assertIn('project_url', dir(a))
        self.assertIn('project_repository', dir(a))
        self.assertIn('license', dir(a))
        self.assertIn('license_url', dir(a))
        self.assertIn('css_files', dir(a))
        self.assertIn('js_files', dir(a))
        self.assertIn('headers', dir(a))
        self.assertIn('extended_classes', dir(a))
