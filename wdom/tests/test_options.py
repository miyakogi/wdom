#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from copy import copy
import logging
from unittest import TestCase
from importlib import reload

import pytest

from wdom.options import parse_command_line, config
from wdom.log import configure_logger
from wdom import tag
from wdom import themes

_argv = copy(sys.argv)
_config = copy(vars(config))


def teardown_function(function):
    sys.argv = copy(_argv)
    for k, v in _config.items():
        setattr(config, k, v)


def test_default_loglevel():
    parse_command_line()
    configure_logger()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == logging.INFO


@pytest.mark.parametrize('level, expected',
                         [('debug', logging.DEBUG),
                          ('info', logging.INFO),
                          ('warn', logging.WARN),
                          ('error', logging.ERROR),
                          ])
def test_loglevel(level, expected):
    sys.argv.extend(['--logging', level])
    parse_command_line()
    configure_logger()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == expected


def test_debug_without_logging():
    sys.argv.extend(['--debug'])
    parse_command_line()
    configure_logger()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_debug_with_logging():
    sys.argv.extend(['--debug', '--logging', 'warn'])
    parse_command_line()
    configure_logger()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == logging.WARN


class TestThemeOption(TestCase):
    def tearDown(self):
        sys.argv = copy(_argv)
        for k, v in _config.items():
            setattr(config, k, v)

    def test_no_theme(self):
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(themes)
        self.assertEqual(len(log.output), 1)
        self.assertTrue(log.records[0].msg.startswith('No theme'))
        self.assertTrue(log.records[0].msg.endswith('Use default theme.'))
        self.assertEqual(themes.Button, tag.Button)

    def test_bs(self):
        sys.argv.extend(['--theme', 'bootstrap3'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(themes)
        self.assertEqual(len(log.output), 1)
        self.assertEqual(log.records[0].msg, 'Use theme: bootstrap3')
        from wdom.themes import bootstrap3
        self.assertEqual(themes.Button, bootstrap3.Button)

    def test_unknown_theme(self):
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
