#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
from tempfile import NamedTemporaryFile
from copy import copy
import logging
import unittest
from importlib import reload
import subprocess

from nose_parameterized import parameterized

from wdom.misc import root_dir
from wdom.options import parse_command_line, config, set_loglevel
from wdom import tag
from wdom.themes import default as default_theme
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
        src = '\n'.join([
            'import sys',
            'sys.path.append(\'{}\')'.format(path.dirname(root_dir)),
            'from wdom import options',
        ])
        with NamedTemporaryFile('w', dir=path.abspath(path.curdir)) as f:
            f.write(src)
            f.flush()  # save file
            cmd = [sys.executable, f.name, '--test-arg']
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            proc.wait()
        result = proc.stdout.read()
        self.assertIn('usage: WDOM', result)
        self.assertIn('Unknown Argument', result)
        self.assertIn('--test-arg', result)


class TestThemeOption(unittest.TestCase):
    def tearDown(self):
        reset_options()
        super().tearDown()

    def test_no_theme(self):
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(default_theme)
        self.assertEqual(len(log.output), 1)
        self.assertTrue(log.records[0].msg.startswith('No theme'))
        self.assertTrue(log.records[0].msg.endswith('Use default theme.'))
        self.assertEqual(default_theme.Button, tag.Button)

    def test_bs(self):
        sys.argv.extend(['--theme', 'bootstrap3'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(default_theme)
        self.assertEqual(len(log.output), 1)
        self.assertEqual(log.records[0].msg, 'Use theme: bootstrap3')
        from wdom.themes import bootstrap3
        self.assertEqual(default_theme.Button, bootstrap3.Button)

    def test_unknown_theme(self):
        sys.argv.extend(['--theme', 'unknown'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'WARN') as log:
            reload(default_theme)
        self.assertEqual(len(log.output), 2)
        self.assertTrue(log.records[0].msg.startswith('Unknown theme'))
        self.assertTrue(log.records[1].msg.startswith('Available themes:'))
        self.assertIn('unknown', log.records[0].msg)
        self.assertIn('skeleton', log.records[1].msg)
        self.assertEqual(default_theme.Button, tag.Button)


if __name__ == '__main__':
    unittest.main()
