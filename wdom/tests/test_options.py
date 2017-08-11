#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from copy import copy
import logging
import unittest
from importlib import reload

from parameterized import parameterized

from wdom.options import parse_command_line, config, set_loglevel
from wdom import tag
from wdom.testing import TestCase

_argv = copy(sys.argv)
_config = copy(vars(config))


def reset_options():
    sys.argv = copy(_argv)
    for k, v in _config.items():
        setattr(config, k, v)


class TestOptions(TestCase):
    def tearDown(self):
        reset_options()
        super().tearDown()

    def test_default_loglevel(self):
        parse_command_line()
        set_loglevel()
        logger = logging.getLogger('wdom')
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)

    @parameterized.expand([
        ('debug', logging.DEBUG),
        ('info', logging.INFO),
        ('warn', logging.WARN),
        ('error', logging.ERROR),
    ])
    def test_loglevel(self, level_name, level):
        sys.argv.extend(['--logging', level_name])
        parse_command_line()
        logger = logging.getLogger('wdom')
        self.assertEqual(logger.getEffectiveLevel(), level)
        reset_options()

    def test_debug_without_logging(self):
        sys.argv.extend(['--debug'])
        parse_command_line()
        logger = logging.getLogger('wdom')
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)

    def test_debug_with_logging(self):
        sys.argv.extend(['--debug', '--logging', 'warn'])
        parse_command_line()
        logger = logging.getLogger('wdom')
        assert logger.getEffectiveLevel() == logging.WARN

    def test_unknown_args(self):
        sys.argv.extend(['--test-args', 'a'])
        # no error/log when get unknown args
        with self.assertRaises(AssertionError):
            with self.assertLogs('wdom'):
                parse_command_line()


class TestThemeOption(unittest.TestCase):
    def setUp(self):
        super().setUp()
        from wdom.themes import default
        self.theme_mod = default

    def tearDown(self):
        reset_options()
        super().tearDown()

    def test_no_theme(self):
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO'):
            # should be no log
            reload(self.theme_mod)

    def test_bs(self):
        sys.argv.extend(['--theme', 'bootstrap3'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(self.theme_mod)
        self.assertEqual(len(log.output), 1)
        self.assertEqual(log.records[0].msg, 'Use theme: bootstrap3')
        from wdom.themes import bootstrap3
        self.assertEqual(self.theme_mod.Button, bootstrap3.Button)

    def test_unknown_theme(self):
        sys.argv.extend(['--theme', 'unknown'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'WARN') as log:
            reload(self.theme_mod)
        self.assertEqual(len(log.output), 2)
        self.assertTrue(log.records[0].msg.startswith('Unknown theme'))
        self.assertTrue(log.records[1].msg.startswith('Available themes:'))
        self.assertIn('unknown', log.records[0].msg)
        self.assertIn('skeleton', log.records[1].msg)
        self.assertEqual(self.theme_mod.Button, tag.Button)


if __name__ == '__main__':
    unittest.main()
