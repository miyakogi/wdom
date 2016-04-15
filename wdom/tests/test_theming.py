#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from copy import copy
from unittest import TestCase
from importlib import reload

from wdom.options import parse_command_line, config
from wdom import tag
from wdom import themes


class TestThemeOption(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._argv = copy(sys.argv)
        cls._config = copy(vars(config))

    def tearDown(self):
        sys.argv = copy(self._argv)
        for k, v in self._config.items():
            setattr(config, k, v)

    def test_no_theme(self):
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(themes)
        self.assertEqual(len(log.output), 1)
        self.assertTrue(log.records[0].msg.startswith('No theme'))
        self.assertTrue(log.records[0].msg.endswith('Use default theme.'))
        self.assertEqual(themes.Button, tag.Button)

    def test_bs(self) -> None:
        sys.argv.extend(['--theme', 'bootstrap3'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(themes)
        self.assertEqual(len(log.output), 1)
        self.assertEqual(log.records[0].msg, 'Use theme: bootstrap3')
        from wdom.themes import bootstrap3
        self.assertEqual(themes.Button, bootstrap3.Button)

    def test_unknown_theme(self) -> None:
        sys.argv.extend(['--theme', 'unknown'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'WARN') as log:
            reload(themes)
        self.assertEqual(len(log.output), 2)
        self.assertTrue(log.records[0].msg.startswith('Unknown theme'))
        self.assertTrue(log.records[1].msg.startswith('Available themes:'))
        self.assertIn('unknown', log.records[0].msg)
        self.assertIn('skeleton', log.records[1].msg)
        self.assertEqual(themes.Button, tag.Button)
